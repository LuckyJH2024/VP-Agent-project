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

## Project Structure

```
vet_kg/
├── src/                    # Source code directory
│   ├── preprocess.py      # Data preprocessing script
│   └── kg_builder.py      # Knowledge graph construction script
│
├── data/                   # Data directory
│   ├── raw/               # Raw input data
│   │   └── *.txt         # Original text files
│   └── processed/         # Processed data
│       └── drug_data.json # Structured JSON output
│
├── reports/               # Generated reports directory
│   ├── kg_report.yaml    # Statistical analysis report
│   └── visualizations/   # Graph visualizations
│       └── *.png        # Generated graph images
│
├── logs/                  # Log files directory
│   └── vet_kg.log       # Processing and error logs
│
├── config.yaml           # Configuration file
├── requirements.txt      # Project dependencies
└── README.md            # This documentation
```

## Installation

1. Create project structure:
```bash
mkdir -p vet_kg/{src,data,reports,logs}
```

2. Create and activate a virtual environment:
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

## Configuration

The `config.yaml` file controls all aspects of the system:

```yaml
neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "your_password"

data:
  input_file: "data/your_file.txt"
  processed_file: "data/drug_data.json"

logging:
  level: "INFO"
  file: "logs/vet_kg.log"

visualization:
  figure_size: [12, 8]
  node_size: 1500
  font_size: 8
```

## Working with Data

### Initial Setup
1. Place your initial data file in `vet_kg/data/`:
```bash
cp your_data.txt vet_kg/data/
```

2. Update the input file path in `config.yaml`:
```yaml
data:
  input_file: "data/your_data.txt"
```

### Processing Data
1. Run the preprocessing script:
```bash
python src/preprocess.py
```
This will:
- Clean and structure the raw text data
- Extract medical entities
- Generate `drug_data.json` in the data directory

2. Build the knowledge graph:
```bash
python src/kg_builder.py
```
This will:
- Create Neo4j constraints
- Build the knowledge graph
- Detect communities
- Generate reports and visualizations

### Adding New Data
1. Backup existing data (recommended):
```bash
cp data/drug_data.json data/drug_data_backup.json
```

2. Place new data file:
```bash
cp new_data.txt vet_kg/data/
```

3. Update configuration and process:
- Edit `config.yaml` with new file path
- Run preprocessing and building scripts

### Data Processing Modes

1. **Append Mode** (Default):
   - Uses Neo4j `MERGE` commands
   - Updates existing nodes and relationships
   - Adds new data without deleting existing
   - Preserves graph structure

2. **Clean Rebuild**:
   - Clear existing data:
   ```cypher
   MATCH (n) DETACH DELETE n
   ```
   - Run processing scripts for complete rebuild

## Accessing Results

### 1. Processed Data
- Location: `vet_kg/data/drug_data.json`
- Format: Structured JSON
- Contents: Cleaned and extracted entities

### 2. Knowledge Graph
- Access: Neo4j Browser (http://localhost:7474)
- Credentials: From config.yaml
- Example queries:
```cypher
// View all drugs
MATCH (d:Drug) RETURN d

// Get drug relationships
MATCH (d:Drug)-[r]->(n) RETURN d, r, n
```

### 3. Reports and Visualizations
- Statistical Report: `reports/kg_report.yaml`
- Graph Visualization: `reports/kg_report_visualization.png`
- Contents:
  - Node and relationship counts
  - Community statistics
  - Graph structure analysis

### 4. Logs
- Location: `logs/vet_kg.log`
- Contents:
  - Processing steps
  - Errors and warnings
  - Performance metrics

## Troubleshooting

### Common Issues

1. **Neo4j Connection**:
   - Verify Neo4j is running: `neo4j status`
   - Check credentials in config.yaml
   - Test connection: http://localhost:7474

2. **Data Processing**:
   - Check input file format
   - Verify file paths in config.yaml
   - Review logs for errors

3. **Memory Issues**:
   - Reduce batch size in config
   - Monitor Neo4j memory usage
   - Check available system resources

### Error Resolution
1. Check the log file: `logs/vet_kg.log`
2. Verify file permissions
3. Ensure all dependencies are installed
4. Check Neo4j database status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your chosen license]

## Contact

[Your contact information]