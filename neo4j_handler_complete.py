import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

class Neo4jHandler:
    """Manages connections and operations with Neo4j database."""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """Initialize Neo4j driver connection."""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._stats = {
            'queries_executed': 0,
            'queries_failed': 0,
            'total_query_time': 0.0
        }
        self.connect()
        self._setup_constraints()

    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")

    def _setup_constraints(self):
        """Setup necessary database constraints."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Technique) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Tactic) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ThreatGroup) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Malware) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Tool) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:CVE) REQUIRE n.id IS UNIQUE"
        ]
        for query in constraints:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.warning(f"Failed to setup constraint: {e}")

    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if parameters is None:
            parameters = {}
            
        import time
        start_time = time.time()
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = [record.data() for record in result]
                
            self._stats['queries_executed'] += 1
            self._stats['total_query_time'] += (time.time() - start_time)
            return records
            
        except Exception as e:
            self._stats['queries_failed'] += 1
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {parameters}")
            raise

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the graph."""
        stats = {}
        
        try:
            # Get node count
            result = self.execute_query("MATCH (n) RETURN count(n) as node_count")
            stats['node_count'] = result[0]['node_count'] if result else 0
            
            # Get relationship count
            result = self.execute_query("MATCH ()-[r]->() RETURN count(r) as relationship_count")
            stats['relationship_count'] = result[0]['relationship_count'] if result else 0
            
            # Get node types distribution
            result = self.execute_query("MATCH (n) RETURN labels(n)[0] as type, count(n) as count")
            stats['node_types'] = {record['type']: record['count'] for record in result if record['type']}
            
            # Get relationship types distribution
            result = self.execute_query("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
            stats['relationship_types'] = {record['type']: record['count'] for record in result if record['type']}
            
            # Add handler stats
            stats['handler_stats'] = self._stats
            
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            
        return stats

    def get_nodes(self, limit: int = 100, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve nodes, optionally filtered by type."""
        query = "MATCH (n"
        if node_type:
            query += f":{node_type}"
        query += f") RETURN n LIMIT {limit}"
        
        try:
            results = self.execute_query(query)
            # Flatten the neo4j node format somewhat for easier display
            nodes = []
            for record in results:
                node = record.get('n', {})
                if isinstance(node, dict):
                    nodes.append(node)
                elif hasattr(node, '_properties'): # if it's a Neo4j Node object
                   nodes.append(dict(node))
            return nodes
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return []

    def export_for_3d_visualization(self, limit: int = 500, node_types: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """Export graph data in format expected by 3d-force-graph format."""
        
        type_filter = ""
        if node_types and len(node_types) > 0:
            type_filter = f"WHERE labels(n)[0] IN {node_types} "
            
        query = f"""
        MATCH (n)
        {type_filter}
        WITH n LIMIT {limit}
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        
        nodes_dict = {}
        links = []
        
        try:
            results = self.execute_query(query)
            
            for record in results:
                # Add source node
                n = record.get('n')
                if n:
                    node_id = n.get('id') or n.element_id
                    if node_id not in nodes_dict:
                        labels = list(n.labels) if hasattr(n, 'labels') else ['Unknown']
                        label = labels[0] if labels else 'Unknown'
                        nodes_dict[node_id] = {
                            "id": node_id,
                            "name": n.get('name') or n.get('title') or str(node_id),
                            "label": label,
                            "description": n.get('description', ''),
                            "color": self._get_color_for_label(label)
                        }
                
                # Add target node and relationship
                r = record.get('r')
                m = record.get('m')
                if r and m:
                    target_id = m.get('id') or m.element_id
                    if target_id not in nodes_dict:
                         labels = list(m.labels) if hasattr(m, 'labels') else ['Unknown']
                         label = labels[0] if labels else 'Unknown'
                         nodes_dict[target_id] = {
                            "id": target_id,
                            "name": m.get('name') or m.get('title') or str(target_id),
                            "label": label,
                            "description": m.get('description', ''),
                            "color": self._get_color_for_label(label)
                         }
                    
                    source_id = n.get('id') or n.element_id
                    links.append({
                        "source": source_id,
                        "target": target_id,
                        "label": r.type if hasattr(r, 'type') else str(type(r))
                    })
                    
            return {
                "nodes": list(nodes_dict.values()),
                "links": links
            }
            
        except Exception as e:
            logger.error(f"Failed to export for 3d visualization: {e}")
            return {"nodes": [], "links": []}

    def _get_color_for_label(self, label: str) -> str:
        """Assign colors to node types for visualization."""
        colors = {
            "Technique": "#E74C3C",    # Red
            "Tactic": "#3498DB",       # Blue
            "ThreatGroup": "#9B59B6",  # Purple
            "Malware": "#E67E22",      # Orange
            "Tool": "#2ECC71",         # Green
            "CVE": "#F1C40F",          # Yellow
            "Unknown": "#BDC3C7"       # Gray
        }
        return colors.get(label, colors["Unknown"])
