---
tool_name: web_search
description: Search the web for information
category: search
arguments:
  - name: query
    type: string
    description: Search query
  - name: num_results
    type: integer
    description: "Number of results to return (default: 5)"
---

# Web Search Tool

This tool searches the web for information.

## Usage

Provide a search query and optionally specify the number of results.

## Example Input

```json
{
  "query": "latest advances in artificial intelligence 2024",
  "num_results": 10
}
```

## Output Format

Returns a list of search results with:
- Title
- URL
- Snippet/description
- Relevance score
