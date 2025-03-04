from neo4j import GraphDatabase
import yaml
import json
import ast
import logging
import os

class DataImporter:
    def __init__(self, config_path="../config.yaml"):
        self.load_config(config_path)
        self.setup_logging()
        self.connect_to_neo4j()

    def load_config(self, config_path):
        """Load configuration from yaml file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def setup_logging(self):
        """Set up logging configuration."""
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'chatbot.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=self.config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect_to_neo4j(self):
        """Connect to Neo4j database."""
        neo4j_config = self.config['neo4j']
        self.driver = GraphDatabase.driver(
            neo4j_config['uri'],
            auth=(neo4j_config['user'], neo4j_config['password'])
        )

    def read_drug_data(self):
        """Read drug data from input file."""
        input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                self.config['data']['input_file'])
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Safely evaluate the string representation of the list of dictionaries
                drug_data = ast.literal_eval(content)
                if isinstance(drug_data, dict):
                    drug_data = [drug_data]
                return drug_data
        except Exception as e:
            self.logger.error(f"Error reading drug data: {str(e)}")
            return []

    def import_drug_data(self):
        """Import drug data into Neo4j."""
        drug_data = self.read_drug_data()
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            for drug in drug_data:
                try:
                    # Create drug node
                    session.run("""
                        CREATE (d:Drug {
                            name: $name,
                            uses: $uses,
                            contraindications: $contraindications,
                            adverse_effects: $adverse_effects,
                            storage: $storage
                        })
                    """, {
                        'name': drug['Medicine Name'],
                        'uses': drug.get('Uses/Indications', ''),
                        'contraindications': drug.get('Contraindications/Precautions/Warnings', ''),
                        'adverse_effects': drug.get('Adverse Effects', ''),
                        'storage': drug.get('Storage/Stability', '')
                    })
                    
                    self.logger.info(f"Imported drug: {drug['Medicine Name']}")
                except Exception as e:
                    self.logger.error(f"Error importing drug {drug.get('Medicine Name', 'unknown')}: {str(e)}")

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

def main():
    importer = DataImporter()
    try:
        importer.import_drug_data()
    finally:
        importer.close()

if __name__ == "__main__":
    main() 