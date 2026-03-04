---
tool_name: content_summarizer
description: Summarize long content into concise summaries
category: research
arguments:
  - name: content
    type: string
    description: Content to summarize
  - name: max_length
    type: integer
    description: Maximum summary length in words
  - name: style
    type: string
    description: Summary style (brief, detailed, bullet_points)
---

# Content Summarizer Tool

This tool summarizes long content into concise, digestible summaries.

## Usage

Provide the content to summarize and specify preferences.

## Summary Styles

- **brief**: Short, high-level summary (50-100 words)
- **detailed**: Comprehensive summary (200-500 words)
- **bullet_points**: Key points in bullet format

## Example Input

```json
{
  "content": "Long article text...",
  "max_length": 200,
  "style": "detailed"
}
```

## Output

Returns a well-structured summary preserving key information.
