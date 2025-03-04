from neo4j import GraphDatabase
from typing import List, Dict, Any
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import yaml
import re

class VetPharmacyBot:
    def __init__(self, config_path: str = "../config.yaml"):
        """Initialize the veterinary pharmacy chatbot."""
        self.load_config(config_path)
        self.setup_logging()
        self.setup_models()
        self.connect_to_neo4j()

    def load_config(self, config_path: str):
        """Load configuration from yaml file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/chatbot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_models(self):
        """Initialize NLP models."""
        self.nlp = spacy.load("en_core_web_sm")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def connect_to_neo4j(self):
        """Connect to Neo4j database."""
        neo4j_config = self.config['neo4j']
        self.driver = GraphDatabase.driver(
            neo4j_config['uri'],
            auth=(neo4j_config['user'], neo4j_config['password'])
        )

    def process_query(self, user_query: str) -> str:
        """Process user query and generate response."""
        # Extract intent and entities
        intent, entities = self._analyze_query(user_query)
        
        # Get relevant information from knowledge graph
        kg_info = self._query_knowledge_graph(intent, entities)
        
        # Generate response
        response = self._generate_response(intent, entities, kg_info)
        
        return response

    def _analyze_query(self, query: str) -> tuple:
        """Analyze user query to extract intent and entities."""
        doc = self.nlp(query.lower())
        
        # Define intent patterns
        intent_patterns = {
            'usage': r'(how|what|when).*(use|give|administer|dose|dosage)',
            'side_effects': r'(side effects|adverse|reactions|problems)',
            'contraindications': r'(contraindications|warnings|cautions|avoid)',
            'interactions': r'(interact|combination|mixed|together)',
            'storage': r'(store|storage|keep|stability)',
        }
        
        # Determine intent
        intent = 'general'
        for intent_name, pattern in intent_patterns.items():
            if re.search(pattern, query.lower()):
                intent = intent_name
                break
        
        # Extract entities (drug names, animal types, symptoms)
        entities = {
            'drugs': [],
            'animals': [],
            'symptoms': []
        }
        
        for ent in doc.ents:
            if ent.label_ in ['CHEMICAL', 'PRODUCT']:
                entities['drugs'].append(ent.text)
            elif ent.label_ in ['ANIMAL']:
                entities['animals'].append(ent.text)
            elif ent.label_ in ['DISEASE', 'SYMPTOM']:
                entities['symptoms'].append(ent.text)
        
        return intent, entities

    def _query_knowledge_graph(self, intent: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Query Neo4j knowledge graph based on intent and entities."""
        with self.driver.session() as session:
            if intent == 'usage':
                return self._query_usage(session, entities)
            elif intent == 'side_effects':
                return self._query_side_effects(session, entities)
            elif intent == 'contraindications':
                return self._query_contraindications(session, entities)
            elif intent == 'interactions':
                return self._query_interactions(session, entities)
            elif intent == 'storage':
                return self._query_storage(session, entities)
            else:
                return self._query_general(session, entities)

    def _query_usage(self, session, entities):
        """Query usage information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})
                OPTIONAL MATCH (d)-[:HAS_DOSAGE]->(dos:Dosage)
                RETURN d.uses as uses, dos.description as dosage
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _query_side_effects(self, session, entities):
        """Query side effects information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})
                OPTIONAL MATCH (d)-[:HAS_SIDE_EFFECT]->(e:Effect)
                RETURN d.adverse_effects as effects, collect(e.name) as specific_effects
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _query_contraindications(self, session, entities):
        """Query contraindications information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})
                OPTIONAL MATCH (d)-[:CONTRAINDICATED_FOR]->(c:Contraindication)
                RETURN d.contraindications as warnings, collect(c.name) as specific_contraindications
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _query_interactions(self, session, entities):
        """Query drug interactions information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d1:Drug {name: $drug_name})
                OPTIONAL MATCH (d1)-[r:INTERACTS_WITH]-(d2:Drug)
                RETURN collect(d2.name) as interacting_drugs
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _query_storage(self, session, entities):
        """Query storage information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})
                RETURN d.storage as storage
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _query_general(self, session, entities):
        """Query general drug information."""
        if entities['drugs']:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})
                RETURN d
                """, drug_name=entities['drugs'][0])
            return result.single()
        return {}

    def _generate_response(self, intent: str, entities: Dict[str, List[str]], kg_info: Dict[str, Any]) -> str:
        """Generate natural language response based on intent and knowledge graph information."""
        if not kg_info:
            return "I'm sorry, I couldn't find information about that drug. Could you please verify the drug name?"

        if intent == 'usage':
            return self._format_usage_response(kg_info)
        elif intent == 'side_effects':
            return self._format_side_effects_response(kg_info)
        elif intent == 'contraindications':
            return self._format_contraindications_response(kg_info)
        elif intent == 'interactions':
            return self._format_interactions_response(kg_info)
        elif intent == 'storage':
            return self._format_storage_response(kg_info)
        else:
            return self._format_general_response(kg_info)

    def _format_usage_response(self, info):
        """Format usage information response."""
        response = []
        if info.get('uses'):
            response.append(f"Usage Information:\n{info['uses']}")
        if info.get('dosage'):
            response.append(f"\nDosage Instructions:\n{info['dosage']}")
        return "\n".join(response) if response else "I couldn't find specific usage information for this drug."

    def _format_side_effects_response(self, info):
        """Format side effects information response."""
        if info.get('effects'):
            return f"Potential side effects:\n{info['effects']}"
        return "I couldn't find specific side effect information for this drug."

    def _format_contraindications_response(self, info):
        """Format contraindications information response."""
        if info.get('warnings'):
            return f"Important warnings and contraindications:\n{info['warnings']}"
        return "I couldn't find specific contraindication information for this drug."

    def _format_interactions_response(self, info):
        """Format drug interactions information response."""
        if info.get('interacting_drugs'):
            drugs = ", ".join(info['interacting_drugs'])
            return f"This drug may interact with: {drugs}"
        return "No specific drug interaction information found."

    def _format_storage_response(self, info):
        """Format storage information response."""
        if info.get('storage'):
            return f"Storage instructions:\n{info['storage']}"
        return "I couldn't find specific storage information for this drug."

    def _format_general_response(self, info):
        """Format general drug information response."""
        if info:
            return f"Here's what I know about this drug:\n{info}"
        return "I couldn't find general information about this drug."

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

def main():
    # Example usage
    bot = VetPharmacyBot()
    
    # Example queries
    example_queries = [
        "What is the dosage of ACARBOSE for dogs?",
        "What are the side effects of ACARBOSE?",
        "How should I store ACARBOSE?",
        "What are the contraindications for ACARBOSE in cats?",
    ]
    
    try:
        for query in example_queries:
            print(f"\nQuery: {query}")
            response = bot.process_query(query)
            print(f"Response: {response}")
    finally:
        bot.close()

if __name__ == "__main__":
    main() 