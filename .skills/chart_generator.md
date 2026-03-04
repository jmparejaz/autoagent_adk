---
tool_name: chart_generator
description: Generate charts and visualizations from data
category: analysis
arguments:
  - name: data
    type: object
    description: Data to visualize
  - name: chart_type
    type: string
    description: Type of chart (bar, line, pie, scatter)
---

# Chart Generator Tool

This tool generates charts and visualizations from data.

## Usage

Provide data and specify the chart type.

## Supported Chart Types

- **bar**: Bar charts for comparing categories
- **line**: Line charts for trends over time
- **pie**: Pie charts for proportional data
- **scatter**: Scatter plots for correlations
- **area**: Area charts for cumulative data

## Example Input

```json
{
  "data": [10, 20, 30, 40],
  "chart_type": "bar",
  "labels": ["Q1", "Q2", "Q3", "Q4"]
}
```
