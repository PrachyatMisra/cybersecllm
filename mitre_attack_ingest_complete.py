import logging
import requests
import json
from typing import Dict, Any, List
from neo4j_handler_complete import Neo4jHandler

logger = logging.getLogger(__name__)

class MitreAttackIngester:
    """Ingests MITRE ATT&CK STIX 2.1 data into Neo4j"""

    STIX_URLS = {
        "enterprise": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
        "mobile": "https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json",
        "ics": "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json"
    }

    def __init__(self, neo4j_handler: Neo4jHandler, matrix: str = "enterprise"):
        self.handler = neo4j_handler
        self.matrix = matrix
        if matrix not in self.STIX_URLS:
            raise ValueError(f"Unknown matrix '{matrix}'. Choose from {list(self.STIX_URLS.keys())}")
        self.stix_data = None

    def fetch_data(self):
        """Fetch STIX data from MITRE repo."""
        logger.info(f"Fetching {self.matrix} ATT&CK data...")
        response = requests.get(self.STIX_URLS[self.matrix])
        response.raise_for_status()
        self.stix_data = response.json()
        logger.info("Successfully fetched ATT&CK data.")

    def ingest_all(self, include_deprecated: bool = False) -> Dict[str, int]:
        """Parse STIX bundle and ingest nodes and relationships."""
        if not self.stix_data:
            self.fetch_data()

        objects = self.stix_data.get('objects', [])
        
        # Filter out deprecated/revoked if requested
        if not include_deprecated:
            objects = [
                obj for obj in objects 
                if not obj.get('revoked', False) and not obj.get('x_mitre_deprecated', False)
            ]

        stats = {
            'techniques_added': 0,
            'tactics_added': 0,
            'groups_added': 0,
            'malware_added': 0,
            'tools_added': 0,
            'mitigations_added': 0,
            'relationships_added': 0
        }

        # 1. First pass: Create nodes
        logger.info("Ingesting nodes...")
        for obj in objects:
            obj_type = obj.get('type')
            
            if obj_type == 'attack-pattern': # Technique
                self._ingest_technique(obj)
                stats['techniques_added'] += 1
                
            elif obj_type == 'x-mitre-tactic': # Tactic
                self._ingest_tactic(obj)
                stats['tactics_added'] += 1
                
            elif obj_type == 'intrusion-set': # Threat Group
                self._ingest_group(obj)
                stats['groups_added'] += 1
                
            elif obj_type == 'malware':
                self._ingest_software(obj, "Malware")
                stats['malware_added'] += 1
                
            elif obj_type == 'tool':
                self._ingest_software(obj, "Tool")
                stats['tools_added'] += 1
                
            elif obj_type == 'course-of-action': # Mitigation
                self._ingest_mitigation(obj)
                stats['mitigations_added'] += 1

        # 2. Second pass: Create relationships
        logger.info("Ingesting relationships...")
        for obj in objects:
            if obj.get('type') == 'relationship':
                if self._ingest_relationship(obj):
                     stats['relationships_added'] += 1

        logger.info(f"Ingestion complete. Stats: {stats}")
        return stats

    def _get_external_id(self, obj: Dict) -> str:
        """Extract MITRE ID (e.g., T1548) from external references."""
        ext_refs = obj.get('external_references', [])
        for ref in ext_refs:
            if ref.get('source_name') in ['mitre-attack', 'mitre-mobile-attack', 'mitre-ics-attack']:
                return ref.get('external_id', obj.get('id'))
        return obj.get('id')

    def _ingest_technique(self, obj: Dict):
        """Ingest attack-pattern as Technique."""
        mitre_id = self._get_external_id(obj)
        query = """
        MERGE (t:Technique {id: $id})
        SET t.name = $name,
            t.description = $description,
            t.url = $url,
            t.stix_id = $stix_id
        """
        
        url = ""
        for ref in obj.get('external_references', []):
             if ref.get('source_name') in ['mitre-attack', 'mitre-mobile-attack', 'mitre-ics-attack']:
                  url = ref.get('url', '')
                  break

        params = {
            'id': mitre_id,
            'name': obj.get('name', 'Unknown'),
            'description': obj.get('description', ''),
            'url': url,
            'stix_id': obj.get('id')
        }
        self.handler.execute_query(query, params)
        
        # Link to tactics (kill chain phases)
        kill_chain_phases = obj.get('kill_chain_phases', [])
        for phase in kill_chain_phases:
            if phase.get('kill_chain_name') == 'mitre-attack':
                tactic_name = phase.get('phase_name').replace('-', ' ').title()
                tactic_id = phase.get('phase_name') # Rough proxy, actual ID requires tactic object lookup
                
                # We merge tactic here just in case it doesn't exist yet or to link quickly
                rel_query = """
                MATCH (tech:Technique {id: $tech_id})
                MERGE (tac:Tactic {name: $tactic_name})
                MERGE (tech)-[:IN_TACTIC]->(tac)
                """
                self.handler.execute_query(rel_query, {'tech_id': mitre_id, 'tactic_name': tactic_name})

    def _ingest_tactic(self, obj: Dict):
        """Ingest x-mitre-tactic as Tactic."""
        mitre_id = self._get_external_id(obj)
        name = obj.get('name', 'Unknown')
        
        query = """
        MERGE (t:Tactic {name: $name})
        SET t.id = $id,
            t.description = $description,
            t.stix_id = $stix_id
        """
        params = {
            'id': mitre_id,
            'name': name,
            'description': obj.get('description', ''),
            'stix_id': obj.get('id')
        }
        self.handler.execute_query(query, params)

    def _ingest_group(self, obj: Dict):
        """Ingest intrusion-set as ThreatGroup."""
        mitre_id = self._get_external_id(obj)
        query = """
        MERGE (g:ThreatGroup {id: $id})
        SET g.name = $name,
            g.description = $description,
            g.aliases = $aliases,
            g.stix_id = $stix_id
        """
        params = {
            'id': mitre_id,
            'name': obj.get('name', 'Unknown'),
            'description': obj.get('description', ''),
            'aliases': obj.get('aliases', []),
            'stix_id': obj.get('id')
        }
        self.handler.execute_query(query, params)

    def _ingest_software(self, obj: Dict, node_label: str):
        """Ingest malware or tool as Malware/Tool."""
        mitre_id = self._get_external_id(obj)
        query = f"""
        MERGE (s:{node_label} {{id: $id}})
        SET s.name = $name,
            s.description = $description,
            s.labels = $labels,
            s.stix_id = $stix_id
        """
        params = {
            'id': mitre_id,
            'name': obj.get('name', 'Unknown'),
            'description': obj.get('description', ''),
            'labels': obj.get('labels', []),
            'stix_id': obj.get('id')
        }
        self.handler.execute_query(query, params)
        
    def _ingest_mitigation(self, obj: Dict):
        """Ingest course-of-action as Mitigation."""
        mitre_id = self._get_external_id(obj)
        query = """
        MERGE (m:Mitigation {id: $id})
        SET m.name = $name,
            m.description = $description,
            m.stix_id = $stix_id
        """
        params = {
            'id': mitre_id,
            'name': obj.get('name', 'Unknown'),
            'description': obj.get('description', ''),
            'stix_id': obj.get('id')
        }
        self.handler.execute_query(query, params)

    def _ingest_relationship(self, obj: Dict) -> bool:
        """Create a relationship between two STIX objects."""
        source_ref = obj.get('source_ref')
        target_ref = obj.get('target_ref')
        rel_type = obj.get('relationship_type', 'RELATED_TO').replace('-', '_').upper()
        
        # We link based on STIX ID instead of MITRE ID since relationships use STIX internal IDs
        query = f"""
        MATCH (s) WHERE s.stix_id = $source_id
        MATCH (t) WHERE t.stix_id = $target_id
        MERGE (s)-[r:{rel_type}]->(t)
        SET r.description = $description
        RETURN r
        """
        params = {
            'source_id': source_ref,
            'target_id': target_ref,
            'description': obj.get('description', '')
        }
        
        try:
             results = self.handler.execute_query(query, params)
             return len(results) > 0
        except Exception as e:
             logger.warning(f"Failed to create relationship {source_ref} -> {target_ref}: {e}")
             return False
