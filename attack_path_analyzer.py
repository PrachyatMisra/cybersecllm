import logging
from typing import List, Dict, Any
from neo4j_handler_complete import Neo4jHandler

logger = logging.getLogger(__name__)

class AttackPathAnalyzer:
    """Finds potential attack paths through the knowledge graph."""

    def __init__(self, neo4j_handler: Neo4jHandler):
        self.handler = neo4j_handler

    def find_paths(self, start_entity: str, end_entity: str, max_depth: int = 5) -> List[List[str]]:
        """Find attack paths between two entities."""
        logger.info(f"Analyzing paths from '{start_entity}' to '{end_entity}' (max depth: {max_depth})")
        
        # We sanitize the names lightly
        start_entity_clean = start_entity.replace("'", "\\'")
        end_entity_clean = end_entity.replace("'", "\\'")
        
        # Find paths matching start/end names using Neo4j shortestPath
        # It's an undirected graph search up to max_depth hops
        query = f"""
        MATCH (start) WHERE toLower(start.name) CONTAINS toLower('{start_entity_clean}')
        MATCH (end) WHERE toLower(end.name) CONTAINS toLower('{end_entity_clean}')
        MATCH path = allShortestPaths((start)-[*1..{max_depth}]-(end))
        RETURN path LIMIT 25
        """
        
        paths = []
        try:
            results = self.handler.execute_query(query)
            
            for record in results:
                path_obj = record.get('path')
                if path_obj:
                    # Extract node names along the path
                    path_names = []
                    for node in path_obj.nodes:
                         name = node.get('name') or node.get('title') or node.get('id', 'Unknown')
                         path_names.append(name)
                         
                    if path_names and path_names not in paths:
                         paths.append(path_names)
                         
            logger.info(f"Found {len(paths)} unique paths.")
            return paths
            
        except Exception as e:
            logger.error(f"Failed to find attack paths: {e}")
            return []
