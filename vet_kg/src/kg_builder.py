from neo4j import GraphDatabase
import json
import networkx as nx
from community import community_louvain
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import logging
import yaml
from datetime import datetime

class VetKnowledgeGraphBuilder:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize the knowledge graph builder with Neo4j connection details."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.graph = nx.Graph()
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vet_kg.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_constraints(self):
        """Create Neo4j constraints for unique nodes."""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT animal_name IF NOT EXISTS FOR (a:Animal) REQUIRE a.name IS UNIQUE",
                "CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
                "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE"
            ]
            for constraint in constraints:
                session.run(constraint)

    def process_drug_data(self, drug_data: Dict[str, Any]):
        """Process drug data and create nodes and relationships."""
        with self.driver.session() as session:
            # Create Drug node
            drug_query = """
            MERGE (d:Drug {name: $name})
            SET d.storage = $storage,
                d.uses = $uses,
                d.contraindications = $contraindications,
                d.adverse_effects = $adverse_effects
            RETURN d
            """
            session.run(drug_query, {
                'name': drug_data['Medicine Name'],
                'storage': drug_data.get('Storage/Stability', ''),
                'uses': drug_data.get('Uses/Indications', ''),
                'contraindications': drug_data.get('Contraindications/Precautions/Warnings', ''),
                'adverse_effects': drug_data.get('Adverse Effects', '')
            })

            # Process and create relationships
            self._process_uses(session, drug_data)
            self._process_contraindications(session, drug_data)
            self._process_adverse_effects(session, drug_data)
            self._process_dosages(session, drug_data)

    def _process_uses(self, session, drug_data: Dict[str, Any]):
        """Process uses/indications and create relationships."""
        uses = drug_data.get('Uses/Indications', '')
        # Add your text processing logic here to extract diseases and conditions
        # This is a simplified example
        session.run("""
        MATCH (d:Drug {name: $drug_name})
        MERGE (c:Condition {name: $condition})
        MERGE (d)-[:TREATS]->(c)
        """, {'drug_name': drug_data['Medicine Name'], 'condition': uses[:100]})

    def _process_contraindications(self, session, drug_data: Dict[str, Any]):
        """Process contraindications and create relationships."""
        contraindications = drug_data.get('Contraindications/Precautions/Warnings', '')
        # Add your text processing logic here
        session.run("""
        MATCH (d:Drug {name: $drug_name})
        MERGE (c:Contraindication {name: $contraindication})
        MERGE (d)-[:CONTRAINDICATED_FOR]->(c)
        """, {'drug_name': drug_data['Medicine Name'], 'contraindication': contraindications[:100]})

    def _process_adverse_effects(self, session, drug_data: Dict[str, Any]):
        """Process adverse effects and create relationships."""
        effects = drug_data.get('Adverse Effects', '')
        # Add your text processing logic here
        session.run("""
        MATCH (d:Drug {name: $drug_name})
        MERGE (e:Effect {name: $effect})
        MERGE (d)-[:HAS_SIDE_EFFECT]->(e)
        """, {'drug_name': drug_data['Medicine Name'], 'effect': effects[:100]})

    def _process_dosages(self, session, drug_data: Dict[str, Any]):
        """Process dosage information and create relationships."""
        doses = drug_data.get('Doses', '')
        # Add your text processing logic here to extract specific dosages for different animals
        session.run("""
        MATCH (d:Drug {name: $drug_name})
        MERGE (dos:Dosage {description: $dosage})
        MERGE (d)-[:HAS_DOSAGE]->(dos)
        """, {'drug_name': drug_data['Medicine Name'], 'dosage': doses[:100]})

    def detect_communities(self):
        """Detect communities in the knowledge graph using Louvain method."""
        # Convert Neo4j graph to NetworkX graph
        with self.driver.session() as session:
            result = session.run("""
            MATCH (n)-[r]->(m)
            RETURN n.name as source, m.name as target, type(r) as type
            """)
            
            for record in result:
                self.graph.add_edge(record["source"], record["target"], 
                                  relationship=record["type"])

        # Detect communities
        communities = community_louvain.best_partition(self.graph)
        
        # Save community information back to Neo4j
        with self.driver.session() as session:
            for node, community_id in communities.items():
                session.run("""
                MATCH (n) WHERE n.name = $name
                SET n.community = $community
                """, {"name": node, "community": community_id})

        return communities

    def generate_report(self, output_path: str):
        """Generate a comprehensive report about the knowledge graph."""
        with self.driver.session() as session:
            # Collect statistics
            stats = {
                'node_counts': {},
                'relationship_counts': {},
                'communities': {},
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Count nodes by label
            result = session.run("CALL db.labels()")
            for record in result:
                label = record['label']
                count = session.run(f"MATCH (n:{label}) RETURN count(n) as count").single()['count']
                stats['node_counts'][label] = count

            # Count relationships by type
            result = session.run("CALL db.relationshipTypes()")
            for record in result:
                rel_type = record['relationshipType']
                count = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count").single()['count']
                stats['relationship_counts'][rel_type] = count

            # Get community statistics
            result = session.run("""
            MATCH (n)
            WHERE exists(n.community)
            RETURN n.community as community, count(*) as count
            ORDER BY community
            """)
            for record in result:
                stats['communities'][record['community']] = record['count']

            # Generate report
            with open(output_path, 'w') as f:
                yaml.dump(stats, f, default_flow_style=False)

            # Generate visualization
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.graph)
            nx.draw(self.graph, pos, 
                   node_color=list(communities.values()),
                   with_labels=True,
                   node_size=1500,
                   font_size=8)
            plt.savefig(f"{output_path.rsplit('.', 1)[0]}_visualization.png")
            plt.close()

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

def main():
    # Configuration
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "your_password"

    # Initialize builder
    builder = VetKnowledgeGraphBuilder(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # Create constraints
        builder.create_constraints()

        # Load and process drug data
        with open('../data/drug_data.json', 'r') as f:
            drug_data = json.load(f)
            for drug in drug_data:
                builder.process_drug_data(drug)

        # Detect communities
        communities = builder.detect_communities()

        # Generate report
        builder.generate_report('../reports/kg_report.yaml')

    finally:
        builder.close()

if __name__ == "__main__":
    main() 