import json
import re
from typing import Dict, List, Any
import spacy
from tqdm import tqdm

class DrugDataPreprocessor:
    def __init__(self):
        """Initialize the preprocessor with NLP models."""
        self.nlp = spacy.load("en_core_web_sm")
        
    def process_text_file(self, input_file: str) -> List[Dict[str, Any]]:
        """Process the raw text file and convert it to structured data."""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split content into individual drug entries
        drug_entries = self._split_into_drugs(content)
        
        # Process each drug entry
        structured_data = []
        for entry in tqdm(drug_entries, desc="Processing drug entries"):
            processed_entry = self._process_drug_entry(entry)
            if processed_entry:
                structured_data.append(processed_entry)
                
        return structured_data
    
    def _split_into_drugs(self, content: str) -> List[str]:
        """Split the content into individual drug entries."""
        # This is a simplified version - you might need to adjust based on your actual data format
        entries = re.split(r'\n\n(?=\{\'Medicine Name\')', content)
        return [entry.strip() for entry in entries if entry.strip()]
    
    def _process_drug_entry(self, entry: str) -> Dict[str, Any]:
        """Process a single drug entry and convert it to structured format."""
        try:
            # Convert string representation of dictionary to actual dictionary
            drug_dict = eval(entry)
            
            # Clean and structure the data
            cleaned_dict = {}
            for key, value in drug_dict.items():
                # Clean the value
                cleaned_value = self._clean_text(value)
                
                # Extract entities if needed
                if key == 'Uses/Indications':
                    cleaned_dict[key] = cleaned_value
                    cleaned_dict['extracted_conditions'] = self._extract_medical_entities(cleaned_value)
                elif key == 'Adverse Effects':
                    cleaned_dict[key] = cleaned_value
                    cleaned_dict['extracted_effects'] = self._extract_medical_entities(cleaned_value)
                else:
                    cleaned_dict[key] = cleaned_value
                    
            return cleaned_dict
            
        except Exception as e:
            print(f"Error processing entry: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not isinstance(text, str):
            return str(text)
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:()\-\'\"]+', '', text)
        return text.strip()
    
    def _extract_medical_entities(self, text: str) -> List[str]:
        """Extract medical entities from text using spaCy."""
        doc = self.nlp(text)
        # Extract entities that might be medical conditions or symptoms
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['DISEASE', 'SYMPTOM', 'CHEMICAL']:
                entities.append(ent.text)
        return list(set(entities))  # Remove duplicates
    
    def save_to_json(self, data: List[Dict[str, Any]], output_file: str):
        """Save the processed data to a JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # Initialize preprocessor
    preprocessor = DrugDataPreprocessor()
    
    # Process the data
    input_file = '../data/Three_drug_info.txt'
    output_file = '../data/drug_data.json'
    
    # Process and save the data
    processed_data = preprocessor.process_text_file(input_file)
    preprocessor.save_to_json(processed_data, output_file)
    
    print(f"Processed {len(processed_data)} drug entries")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main() 