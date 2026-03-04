---
tool_name: data_query
description: Query and analyze data from databases or files
category: data
arguments:
  - name: query
    type: string
    description: The data query or analysis request
  - name: source
    type: string
    description: Data source (database, file, etc.)
---

# Data Query Tool

This tool allows querying and analyzing data from various sources.

## Usage

Provide a clear data query and the tool will:
1. Parse the query
2. Execute against the data source
3. Return formatted results

## Example Input

```json
{
  "query": "Show me sales trends for Q3",
  "source": "sales_db"
}
```

## Output Format

Results are returned in JSON format with columns and rows.
