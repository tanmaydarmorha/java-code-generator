# Automated Java Code Generation from cURL

**Version:** 1.0  
**Date:** 2025-05-11

---

## Overview

This project automates the generation of Java source code (interface, domain, and concrete classes) from a provided cURL command. It uses LangChain to orchestrate a modular pipeline of LLM-powered tasks that plan, generate, validate, and test the code, with shell and file system tooling for compilation and runtime feedback.

---

## Goals

- Convert cURL input into structured REST operation plans  
- Automatically generate idiomatic Java code based on those plans  
- Compile and validate the generated code using real tools (`javac`, `mvn`)  
- Generate and run unit/integration tests  
- Persist the final code and results  
- Enable feedback loops for self-correction in generation

---

## Architecture

cURL Input
↓
[ Planning Node ]
↓
[ Code Generation Node ]
↓
┌─────────────────────┐
│ Shell + File System │
└────────┬────────────┘
↓
[ Validation Node ] ←── feedback loop ──┐
↓ │
[ Testing Node ] │
↓ │
[ Persist Code + Results ] ◄───────────┘

---


---

## Functional Components

### 1. Planning Node
- **Input:** Raw `cURL` command  
- **Output:** Structured REST operation plan (Markdown)  
- **Responsibilities:**  
  - Parse HTTP method, headers, body  
  - Infer operation name, request/response DTO schemas  
  - Example plan:
    ```markdown
    # API: `http://example.com/users`
    # Operation: `getUser`
    # HTTP Method: `GET`
    # Request Body: `{ "id": 123 }`
    # Response Body: `{ "name": "John Doe", "age": 42 }`
    ```

### 2. Code Generation Node
- **Input:** Structured operation plan  
- **Output:** Java source files (interface, domain classes, implementation stub)  
- **Responsibilities:**  
  - Generate domain classes based on DTO schemas  
  - Define an interface with method signature  
  - Create a concrete implementation class (e.g., using Spring WebClient)

### 3. Validation Node
- **Input:** Generated source files  
- **Output:** Compilation success or error logs  
- **Responsibilities:**  
  - Run `javac` or `mvn compile` inside a sandbox  
  - Capture and return compile-time errors  
  - Provide structured feedback for refinement

### 4. Testing Node
- **Input:** Valid Java code  
- **Output:** Test results, coverage metrics  
- **Responsibilities:**  
  - Generate unit/integration tests based on endpoint logic  
  - Run tests using `mvn test` or `gradle test`  
  - Capture and return test output (pass/fail, errors)

---

## Tools

### Shell Tool
Executes whitelisted shell commands in a secure workspace.  
- **Allowed Commands:** `javac`, `java`, `mvn`, `gradle`, `ls`, `cat`  
- **Security:** Timeouts, command filtering, sandboxed container runtime

### File System Tool
Read/write Java files for code generation and feedback loop.  
- `write(path, content)`  
- `read(path)`  
- Operates in a temporary workspace per execution

---

## Persistence

- Validated Java code and test outputs are archived  
- Optionally commit generated code to a Git repository  
- Log metadata about each run (cURL, success/failure, duration)

---

## Constraints

- Supports simple RESTful endpoints only (no GraphQL or multipart/form-data in v1)  
- DTO field types must be inferrable from example body or headers  
- Maximum of 3 feedback loops before failure exit

---

## Future Enhancements

- Export OpenAPI specifications  
- Support authentication headers and OAuth2  
- CI/CD integration for deploying validated stubs  
- Web UI for visualizing generated code and pipeline status

---
