import logging
from typing import List, Dict, Any, Optional
from neo4j_handler_complete import Neo4jHandler

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Retrieves context from Knowledge Graph to augment LLM generation."""

    def __init__(self, neo4j_handler: Neo4jHandler):
        self.handler = neo4j_handler

    async def retrieve(self, query: str, mode: str = "hybrid") -> List[Dict[str, Any]]:
        """Retrieve relevant context based on user query."""
        logger.info(f"Retrieving context for query: '{query}', mode: {mode}")
        
        # Simple stop-word extraction for basic keyword extraction
        stop_words = {'what', 'are', 'the', 'how', 'is', 'a', 'to', 'in', 'used', 'by', 'common', 'techniques', 'for', 'of', 'and'}
        keywords = [word for word in query.lower().replace('?', '').replace('.', '').split() if word not in stop_words]
        
        context = []
        
        # We don't have a Vector store set up (pgvector/weaviate/neo4j vector idx) in this skeleton,
        # so we rely completely on Graph Full-Text / Keyword matching.
        # "Hybrid" here implies full-text indices and graph traversal.

        if mode in ["hybrid", "graph", "vector"]:
             for keyword in keywords:
                 # Search for nodes matching the query keyword
                 cypher_query = f"""
                 MATCH (n)
                 WHERE toLower(n.name) CONTAINS toLower('{keyword}') OR toLower(n.description) CONTAINS toLower('{keyword}')
                 OPTIONAL MATCH (n)-[r]-(m)
                 RETURN n, r, m LIMIT 5
                 """
                 
                 try:
                     results = self.handler.execute_query(cypher_query)
                     for record in results:
                         n = record.get('n')
                         r = record.get('r')
                         m = record.get('m')
                         
                         if n:
                             context_str = f"Entity: {n.get('name', '')} ({list(n.labels)[0] if hasattr(n, 'labels') else ''}) - {n.get('description', '')}"
                             if m and r:
                                 rel_type = r.type if hasattr(r, 'type') else ''
                                 context_str += f" | {rel_type} -> Entity: {m.get('name', '')} ({list(m.labels)[0] if hasattr(m, 'labels') else ''})"
                             
                             if context_str not in [c.get('text') for c in context]:
                                 context.append({"text": context_str, "relevance": 1.0})
                 except Exception as e:
                     logger.warning(f"Failed to execute retrieval query for keyword '{keyword}': {e}")
                     continue

        # Sort and limit
        logger.info(f"Retrieved {len(context)} context pieces.")
        return context[:10]
