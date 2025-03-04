# Veterinary Knowledge Graph Builder

This project implements a knowledge graph system for veterinary medicine data, focusing on drug information, interactions, and relationships. It processes structured veterinary drug data and builds a comprehensive knowledge graph using Neo4j, with additional features for community detection and visualization.

## Features

- **Data Preprocessing**
  - Text cleaning and normalization
  - Medical entity extraction using SpaCy
  - Structured JSON output generation
  - Automated drug information parsing

- **Knowledge Graph Construction**
  - Neo4j graph database integration
  - Automated node and relationship creation
  - Support for multiple entity types (Drugs, Animals, Symptoms, etc.)
  - Relationship type management

- **Community Detection**
  - Louvain method implementation
  - Community visualization
  - Statistical analysis of communities

- **Reporting and Visualization**
  - Comprehensive statistical reports
  - Graph visualization with matplotlib
  - Node and relationship count tracking
  - Community structure analysis

## Prerequisites

- Python 3.8+
- Neo4j Database (4.0+)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vet_kg
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install SpaCy language model:
```bash
python -m spacy download en_core_web_sm
```

5. Configure Neo4j:
   - Install and start Neo4j database
   - Update `config.yaml` with your Neo4j credentials

## Project Structure

```
vet_kg/
├── src/
│   ├── preprocess.py        # Data preprocessing
│   └── kg_builder.py        # Knowledge graph construction
├── data/
│   ├── Three_drug_info.txt  # Raw input data
│   └── drug_data.json       # Processed data
├── reports/                 # Generated reports and visualizations
├── config.yaml             # Configuration file
├── requirements.txt        # Project dependencies
└── README.md              # This file
```

## Configuration

Edit `config.yaml` to customize:
- Neo4j connection settings
- Input/output file paths
- Logging configuration
- Visualization parameters
- Community detection settings

## Usage

1. Preprocess the raw data:
```bash
python src/preprocess.py
```
This will:
- Clean and structure the raw text data
- Extract medical entities
- Generate a structured JSON file

2. Build the knowledge graph:
```bash
python src/kg_builder.py
```
This will:
- Create Neo4j constraints
- Process drug data
- Build the knowledge graph
- Detect communities
- Generate reports and visualizations

## Output

The system generates several outputs:

1. **Processed Data** (`data/drug_data.json`):
   - Structured drug information
   - Extracted medical entities
   - Cleaned text data

2. **Knowledge Graph** (Neo4j database):
   - Drug nodes and properties
   - Relationships between entities
   - Community assignments

3. **Reports** (`reports/`):
   - Statistical analysis (YAML format)
   - Graph visualizations (PNG format)
   - Community structure analysis

## Neo4j Query Examples

Access the knowledge graph using Cypher queries:

```cypher
// Get all drugs and their uses
MATCH (d:Drug)-[:TREATS]->(c:Condition)
RETURN d.name, c.name

// Find drugs by community
MATCH (d:Drug)
WHERE d.community = 1
RETURN d.name

// Get drug interactions
MATCH (d1:Drug)-[:INTERACTS_WITH]-(d2:Drug)
RETURN d1.name, d2.name
```

## Community Structure

The community detection feature uses the Louvain method to identify clusters of related entities. Communities are:
- Saved in the Neo4j database
- Visualized in the generated graph
- Analyzed in the statistical report

## Extending the System

To add new features:

1. **New Entity Types**:
   - Add constraints in `create_constraints()`
   - Create processing methods in `VetKnowledgeGraphBuilder`

2. **New Relationships**:
   - Add relationship types in processing methods
   - Update visualization parameters if needed

3. **Custom Reports**:
   - Extend `generate_report()` method
   - Add new statistics collection

## Troubleshooting

Common issues and solutions:

1. **Neo4j Connection Issues**:
   - Verify Neo4j is running
   - Check credentials in config.yaml
   - Ensure Neo4j bolt port is accessible

2. **Processing Errors**:
   - Check input data format
   - Verify SpaCy model installation
   - Review log files for details

3. **Memory Issues**:
   - Reduce batch size in processing
   - Optimize graph queries
   - Increase available memory

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

[Your chosen license]

## Contact

[Your contact information] 