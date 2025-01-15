# Kibo Core: Universal Distributed Agent Framework

A framework-agnostic, distributed architecture for orchestrating AI Agents (LangGraph, CrewAI, Agno, etc.) using Ray.

## Architecture

This project follows **Domain-Driven Design (DDD)** principles:

- **Domain (`src/kibo_core/domain`)**: Pure interfaces and entities.
  - `IAgentNode`: Protocol for any agent implementation.
  - `AgentContext`: Rich context object with "Pass-Through" `params` for framework-specific flexibility.
- **Infrastructure (`src/kibo_core/infrastructure`)**:
  - `adapters/`: Concrete implementations for different libraries (LangGraph, CrewAI, etc.).
  - `executors/`: Distributed execution (currently supporting **Ray**).
- **Application (`src/kibo_core/application`)**: 
  - `DistributedWorkflowService`: Coordinate tasks across the cluster.

## Getting Started

### Prerequisites

- `uv` (for package management)
- Python 3.11+ (Tested with 3.13)

### Running the Demo

1. Initialize dependencies:
   ```bash
   uv sync --python 3.13
   ```

2. Run the example:
   ```bash
   uv run --python 3.13 main.py
   ```

## Key Features

- **Distributed by Default**: Uses Ray actors to maintain agent state across a cluster.
- **Agnostic**: Wrap any python agent code in an `IAgentNode` adapter.
- **Context Pass-Through**: Pass arbitrary parameters (e.g., `recursion_limit` for LangGraph) through the domain without polluting the core interfaces.

## Examples

### LangChain with Ollama (Llama 3.1)
```bash
uv run --python 3.13 examples/langchain_example.py
```

### CrewAI with Ollama (Llama 3.1)
```bash
uv run --python 3.13 examples/crewai_example.py
```

## Supported Frameworks

- **LangChain / LangGraph**: Via `LangChainAdapter`.
- **CrewAI**: Via `CrewAIAdapter`.

