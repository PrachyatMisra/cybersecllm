import logging
from typing import Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from neo4j_handler_complete import Neo4jHandler
from llm_entity_extractor import LLMEntityExtractor
from graph_builder import GraphBuilder

logger = logging.getLogger(__name__)

class YouTubeIngester:
    """Extracts entities and relations from YouTube video transcripts."""

    def __init__(self, neo4j_handler: Neo4jHandler, extractor: LLMEntityExtractor, builder: GraphBuilder):
        self.handler = neo4j_handler
        self.extractor = extractor
        self.builder = builder

    async def ingest_video(self, url: str) -> Dict[str, Any]:
        """Fetch transcript, extract entities, and build graph."""
        try:
            video_id = self._extract_video_id(url)
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # Robust Multilingual Support: Fetch available transcripts safely
            try:
                transcript_list_manager = YouTubeTranscriptApi.list_transcripts(video_id)
                # First, try to find an English transcript
                try:
                    transcript = transcript_list_manager.find_transcript(['en'])
                except Exception:
                    # If no English transcript is found, pick the first available one and translate it
                    transcript = next(iter(transcript_list_manager))
                    if transcript.is_translatable:
                        transcript = transcript.translate('en')
            except Exception as e:
                raise ValueError(f"Could not retrieve or translate transcripts. Ensure the video has captions available. Details: {e}")

            try:
                transcript_list = transcript.fetch()
            except Exception as e:
                raise ValueError("Could not parse YouTube captions. The video might have captions disabled or restricted by the uploader.")
                
            full_text = " ".join([entry['text'] for entry in transcript_list])
            
            logger.info(f"Transcript fetched successfully. Length: {len(full_text)} characters.")
            
            # For extremely long videos, we might need chunking. 
            # Given a typical LLM context window (8k), we'll truncate or chunk.
            # Here we just take a chunk for demonstration to avoid long wait times.
            max_chars = 8000
            text_to_process = full_text[:max_chars]
            
            # Extract entities and relations
            stats = await self.builder.build_from_text(text_to_process)
            
            # Create a source node for the video
            video_node = {
                "entity": video_id,
                "type": "Source",
                "id": video_id,
                "url": url,
                "title": f"YouTube Video {video_id}",
                "source_type": "YouTube"
            }
            
            self.builder.create_nodes([video_node])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to ingest YouTube video {url}: {e}")
            raise

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        # Handle youtu.be/ID
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
            
        # Handle youtube.com/watch?v=ID
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
            
        raise ValueError("Invalid YouTube URL format")
