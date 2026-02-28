import logging
from typing import Dict, Any, List
from pypdf import PdfReader
from io import BytesIO

from neo4j_handler_complete import Neo4jHandler
from llm_entity_extractor import LLMEntityExtractor
from graph_builder import GraphBuilder

logger = logging.getLogger(__name__)

class PDFIngester:
    """Extracts entities and relations from PDF documents."""

    def __init__(self, neo4j_handler: Neo4jHandler, extractor: LLMEntityExtractor, builder: GraphBuilder):
        self.handler = neo4j_handler
        self.extractor = extractor
        self.builder = builder

    async def ingest_file(self, file_content: BytesIO) -> Dict[str, Any]:
        """Read PDF, extract entities, and build graph."""
        try:
            reader = PdfReader(file_content)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
                
            logger.info(f"Extracting entities from PDF content of length {len(full_text)}")
            
            # Since texts can be massive, take the first 8000 characters for POC.
            # In a production system, this would chunk the text and process batched
            max_chars = 8000
            text_to_process = full_text[:max_chars]
            
            stats = await self.builder.build_from_text(text_to_process)
            
            # Create a source node for the PDF Document
            doc_node = {
                "entity": "PDF Document",
                "type": "Source",
                "id": f"PDF_{hash(text_to_process)}",
                "source_type": "PDF"
            }
            
            self.builder.create_nodes([doc_node])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to ingest PDF: {e}")
            raise
