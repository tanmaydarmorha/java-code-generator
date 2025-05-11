# Java Code Generator

A sophisticated system that automates the generation of Java source code from cURL commands using LLM-powered agents for planning, code generation, and validation.

## Overview

This project leverages multiple specialized agents to convert cURL commands into fully functional Java code implementations. The system follows a modular architecture where each agent is responsible for a specific part of the code generation pipeline.

## Architecture

The system consists of the following components:

### 1. Planning Agent
- Parses cURL commands into structured REST operation plans
- Extracts HTTP method, headers, URL path, and request body
- Infers appropriate operation names and DTO schemas
- Uses the Qwen model for planning

### 2. Code Generation Agent
- Generates Java source files from structured operation plans
- Creates domain classes, interfaces, and implementation classes
- Uses the CodeLlama model for code generation
- Leverages LangChain's FileManagementToolkit for file operations

### 3. Validation Agent
- Compiles and validates the generated Java code
- Provides detailed feedback on compilation and runtime errors
- Uses the Gemma model for error analysis
- Utilizes LangChain's ShellTool for executing commands

### 4. Orchestrator
- Coordinates the planning, code generation, and validation processes
- Manages the workflow and data flow between agents
- Handles error recovery and feedback loops

## Tools

The system uses the following LangChain tools:

- **Shell Tool**: Executes whitelisted commands (javac, java, mvn, gradle, ls, cat)
- **File System Tool**: Reads and writes Java files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/java-code-generator.git
cd java-code-generator
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ensure you have Ollama installed and the required models available:
   - Qwen for planning
   - CodeLlama for code generation
   - Gemma for validation

## Usage

### Example: Generate Code from a cURL Command

```python
from orchestrator import Orchestrator

# Initialize the orchestrator
orchestrator = Orchestrator()

# Example cURL command
curl_command = '''
curl -X POST "https://api.example.com/users" 
  -H "Content-Type: application/json" 
  -d '{"name": "John Doe", "email": "john@example.com"}'
'''

# Generate and validate Java code
result = orchestrator.process_curl_command(curl_command)

# Print the results
print(f"Generation successful: {result['success']}")
print(f"Generated files: {list(result['files'].keys())}")
```

### Running Individual Agents

You can also use the agents individually:

```python
# Example: Using the Code Generation Agent
from agents.code_generation_agent import CodeGenerationAgent

agent = CodeGenerationAgent()
operation_plan = """
# API: `http://example.com/users`
# Operation: `createUser`
# HTTP Method: `POST`
# Request Body: `{ "name": "John Doe", "email": "john@example.com" }`
# Response Body: `{ "id": 123, "name": "John Doe", "email": "john@example.com" }`
"""

java_files = agent.generate_code(operation_plan)
```

## Constraints

- The system currently supports simple RESTful endpoints
- Field types in DTOs must be inferrable from the cURL command
- The system uses a maximum of 3 feedback loops for self-correction

## License

This project is licensed under the MIT License - see the LICENSE file for details.
