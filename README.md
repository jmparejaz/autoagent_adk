# Nexus ADK Platform

A multimodal and multicapability agentic system built with Google ADK (Agent Development Kit).

## Features

- **File Processing**: Process PDF files, images, and documents
- **Database Integration**: Connect to PostgreSQL for data analysis
- **Data Visualization**: Generate interactive charts and graphs
- **Interactive Maps**: Create maps from location data
- **Knowledge Base**: RAG-based chat with company documents
- **Security Guardrails**: Built-in security checks

## Architecture

```
nexus-adk-platform/
├── backend/
│   ├── agents/          # ADK agents
│   ├── tools/           # Tool implementations
│   ├── config/         # Configuration
│   ├── utils/          # Utilities
│   ├── setup.py        # Modular setup
│   ├── demo.py         # Demo mode
│   └── main.py         # FastAPI application
└── requirements.txt    # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
cd nexus-adk-platform
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
- Set `GOOGLE_API_KEY` for Gemini API access
- Configure database credentials (optional for demo mode)

### 3. Run the Backend

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 4. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Demo Mode

The platform works in demo mode without a database. Use the demo database:

```python
from backend.demo import demo_db, get_demo_data, execute_demo_query

# Get all available tables
tables = demo_db.get_tables()
print(tables)  # ['customers', 'orders', 'products', 'locations', 'sales']

# Execute a query
result = demo_db.execute_query("SELECT * FROM customers LIMIT 5")
print(result)
```

## Adding Custom Components

### Register a Database

```python
from backend.setup import setup

setup.register_database(
    name="my_database",
    connection_string="postgresql://user:pass@localhost:5432/mydb",
    description="My custom database",
    tags=["analytics", "production"]
)
```

### Register a Knowledge Base

```python
setup.register_knowledge_base(
    name="company_docs",
    collection_name="company_documents",
    description="Company documentation",
    chunk_size=1500
)
```

### Register a File Processor

```python
setup.register_file_processor(
    name="excel_processor",
    file_extensions=["xlsx", "xls"],
    processor_type="data",
    description="Excel file processor"
)
```

### Initialize

```python
setup.initialize()
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/chat` | POST | Chat with agents |
| `/ws/chat` | WebSocket | Real-time chat |
| `/api/files/upload` | POST | Upload file |
| `/api/db/tables` | GET | List tables |
| `/api/db/query` | POST | Execute query |
| `/api/knowledge/query` | POST | Query knowledge base |
| `/api/visualize/chart` | POST | Create chart |
| `/api/visualize/map` | POST | Create map |

## Available Tools

### Database Tools
- `execute_sql` - Execute SQL queries
- `list_tables` - List available tables
- `describe_table` - Get table schema
- `get_sample_data` - Get sample rows
- `get_locations_for_map` - Get location data

### Analysis Tools
- `analyze_data_from_query` - Statistical analysis
- `create_visualization` - Generate charts
- `create_interactive_chart` - Create Plotly charts

### Map Tools
- `generate_map` - Create interactive maps
- `create_map_from_json` - Map from JSON data
- `create_heatmap_from_query` - Generate heatmaps

### Knowledge Base Tools
- `query_knowledge_base` - Search knowledge base
- `search_knowledge_base` - Semantic search

### Guardrails
- `check_user_input` - Validate input
- `check_sql_safety` - Check SQL safety
- `check_output_safety` - Verify output

## ADK Agents

The platform includes specialized agents:

1. **Data Analyst Agent**: SQL queries, data analysis, visualizations
2. **Maps Agent**: Geographic data and interactive maps
3. **Knowledge Agent**: Document-based Q&A
4. **Security Agent**: Input/output validation

## Security

- SQL injection prevention
- Prompt injection detection
- PII filtering
- Operation validation

## Requirements

- Python 3.10+
- PostgreSQL (optional for demo mode)
- Google API Key (for Gemini)

## License

MIT
