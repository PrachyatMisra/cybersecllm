import logging
from typing import List, Dict, Any
from neo4j_handler_complete import Neo4jHandler
from llm_entity_extractor import LLMEntityExtractor

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Handles the creation of nodes and relationships in Neo4j."""

    def __init__(self, neo4j_handler: Neo4jHandler, entity_extractor: LLMEntityExtractor = None):
        self.handler = neo4j_handler
        self.extractor = entity_extractor
        
    def create_nodes(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create nodes in Neo4j from a list of entity dictionaries."""
        stats = {'nodes_created': 0, 'failed': 0}
        
        for entity in entities:
            try:
                # Basic validation
                if not entity.get('entity') or not entity.get('type'):
                    logger.warning(f"Skipping invalid entity: {entity}")
                    stats['failed'] += 1
                    continue
                
                name = entity['entity'].strip()
                node_type = entity['type'].strip()
                
                # Sanitize to prevent basic injection
                node_type = ''.join(e for e in node_type if e.isalnum())
                
                # We need an ID for merging to avoid duplicates cleanly if name changes slightly.
                # Here we just use name as id if not provided
                node_id = entity.get('id', name.replace(" ", "_").upper())
                
                properties = {k: v for k, v in entity.items() if k not in ['entity', 'type', 'id']}
                
                query = f"""
                MERGE (n:{node_type} {{id: $id}})
                SET n.name = $name
                """
                
                # Add additional properties dynamically
                for key in properties:
                    safe_key = ''.join(e for e in key if e.isalnum())
                    query += f"SET n.{safe_key} = ${safe_key}\n"
                    
                params = {'id': node_id, 'name': name, **properties}
                
                self.handler.execute_query(query, params)
                stats['nodes_created'] += 1
                
            except Exception as e:
                logger.error(f"Failed to create node {entity}: {e}")
                stats['failed'] += 1
                
        return stats

    def create_relationships(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create relationships between existing nodes."""
        stats = {'relationships_created': 0, 'failed': 0}
        
        for rel in relationships:
            try:
                source = rel.get('source')
                target = rel.get('target')
                rel_type = rel.get('relation', 'RELATED_TO').replace(" ", "_").upper()
                
                if not source or not target:
                    logger.warning(f"Skipping invalid relationship: {rel}")
                    stats['failed'] += 1
                    continue
                    
                properties = {k: v for k, v in rel.items() if k not in ['source', 'target', 'relation']}
                
                # Find nodes by name or ID
                source_identifier = str(source).replace(" ", "_").upper() if not rel.get('source_id') else rel.get('source_id')
                target_identifier = str(target).replace(" ", "_").upper() if not rel.get('target_id') else rel.get('target_id')

                query = f"""
                MATCH (s) WHERE s.id = $source_id OR s.name = $source_name
                MATCH (t) WHERE t.id = $target_id OR t.name = $target_name
                MERGE (s)-[r:{rel_type}]->(t)
                """
                
                for key in properties:
                    safe_key = ''.join(e for e in key if e.isalnum())
                    query += f"SET r.{safe_key} = ${safe_key}\n"
                    
                params = {
                    'source_id': source_identifier,
                    'source_name': source,
                    'target_id': target_identifier,
                    'target_name': target,
                    **properties
                }
                
                self.handler.execute_query(query, params)
                stats['relationships_created'] += 1
                
            except Exception as e:
                logger.error(f"Failed to create relationship {rel}: {e}")
                stats['failed'] += 1
                
        return stats

    async def build_from_text(self, text: str) -> Dict[str, Any]:
        """Extract entities/relations from text using LLM and build graph."""
        if not self.extractor:
            raise ValueError("LLMEntityExtractor not initialized for this GraphBuilder.")
            
        logger.info("Extracting entities and relations from text...")
        entities, relations = await self.extractor.extract_all(text)
        
        node_stats = self.create_nodes(entities)
        rel_stats = self.create_relationships(relations)
        
        return {
            "entities_extracted": len(entities),
            "relations_extracted": len(relations),
            "nodes_created": node_stats['nodes_created'],
            "relationships_created": rel_stats['relationships_created']
        }
