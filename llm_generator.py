import logging
from typing import List, Dict, Any
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)

class LLMGenerator:
    """Generates answers based on user queries and retrieved graph context."""

    def __init__(self, model_name: str = "llama3", temperature: float = 0.1):
        self.model_name = model_name
        self.llm = Ollama(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"Initialized LLM Generator with model: {model_name}")

    async def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Synthesize an answer using LLM."""
        logger.info(f"Generating answer for query: '{query}'")
        
        context_str = "\n".join([item.get('text', '') for item in context])
        
        prompt = f"""You are a cybersecurity expert analyzing a knowledge graph.
Answer the user's question explicitly based on the provided context.
If the context does not contain enough information, state that you don't know based on the graph. Do not hallucinate outside knowledge unless explicitly clarifying.

Context from Knowledge Graph:
{context_str}

User Question:
{query}

Expert Answer:"""

        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"Error: Unable to generate response. Check if Local LLM ({self.model_name}) is running."
