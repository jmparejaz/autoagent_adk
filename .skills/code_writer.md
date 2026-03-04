---
tool_name: code_writer
description: Write code in various programming languages
category: code
arguments:
  - name: language
    type: string
    description: Programming language (python, javascript, java, etc.)
  - name: task
    type: string
    description: Description of what the code should do
  - name: requirements
    type: string
    description: Specific requirements or constraints
---

# Code Writer Tool

This tool writes code based on requirements.

## Usage

Specify the programming language and describe what the code should do.

## Supported Languages

- Python
- JavaScript/TypeScript
- Java
- C/C++
- Go
- Rust
- And many more...

## Example Input

```json
{
  "language": "python",
  "task": "Write a function to calculate fibonacci numbers",
  "requirements": "Should use memoization for efficiency"
}
```

## Output

Returns well-structured, documented code with error handling.
