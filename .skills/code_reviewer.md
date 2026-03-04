---
tool_name: code_reviewer
description: Review code for bugs, style issues, and improvements
category: developer
arguments:
  - name: code
    type: string
    description: Code to review
  - name: language
    type: string
    description: Programming language
---

# Code Reviewer Tool

This tool reviews code for issues and improvements.

## Usage

Provide code to be reviewed.

## Review Criteria

- **Bugs**: Potential bugs and logic errors
- **Security**: Security vulnerabilities
- **Performance**: Performance issues
- **Style**: Code style and conventions
- **Best Practices**: Industry best practices
- **Documentation**: Comments and documentation

## Example Input

```json
{
  "code": "function add(a, b) { return a + b; }",
  "language": "javascript"
}
```

## Output

Detailed review report with:
- Issue severity (critical, warning, info)
- Line numbers
- Suggestions for improvement
