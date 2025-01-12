# Kibo AI Framework

**Kibo** is a powerful and flexible abstraction framework designed to unify the orchestration of AI Agents. It allows developers to define, execute, and combine agents from different underlying libraries (like **Agno**, **LangChain**, **CrewAI**, and **PydanticAI**) within a single, consistent interface.

Kibo goes beyond simple wrapping; it enables **distributed** and **parallel** execution of agents, allowing you to build complex, high-performance AI workflows that scale across multiple nodes or simply run concurrently on a single machine. It also includes a built-in **AI Gateway** (powered by LiteLLM) to manage model access, costs, and observability centrally.

## 🚀 Key Features

*   **Unified Abstraction**: Define agents using a generic `AgentConfig` blueprint. Switch the underlying engine (e.g., from `agno` to `langchain`) just by changing a string configuration, without rewriting application logic.
*   **Multi-Framework Support**: Seamlessly mix and match agents:
    *   **Agno (PhiData)**
    *   **LangChain**
    *   **CrewAI**
    *   **PydanticAI**
    *   **LangGraph**
*   **Distributed & Parallel Execution**: Built on top of **Ray**, Kibo allows you to run agents as distributed actors. Execute heavy workloads in parallel or across a cluster with ease.
*   **Integrated Gateway**: Includes a lightweight proxy server (LiteLLM) to unify API calls to OpenAI, Ollama, Anthropic, etc., simplifying credential management and providing usage telemetry.
*   **Zero-Dependency Definitions**: Define agent behaviors in pure Python data structures (Blueprints), making your agent definitions portable and easy to version control.

## 📦 Installation

Kibo is optimized for use with **uv** for fast and reliable dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/D10S0VSkY-OSS/kiboai.git
    cd kiboai
    ```

2.  **Install dependencies using uv:**
    ```bash
    # Creates virtualenv and installs all dependencies
    uv sync
    ```

## 🛠️ Usage

### 1. The Kibo CLI
Kibo provides a CLI to manage the runtime environment (Ray Cluster) and the AI Gateway.

```bash
# Start the Kibo distributed runtime (Head node)
uv run kibo start --head

# Check cluster status
uv run kibo status

# Start the AI Gateway (Proxy)
uv run kibo proxy start
```

### 2. Creating an Agent (Python SDK)

The core usage involves defining an `AgentConfig` and creating an agent instance.

**Basic Example:**

```python
import os
from kibo_core import AgentConfig, create_agent

# 1. Define the Agent Blueprint
agent_def = AgentConfig(
    name="AnalystBot",
    description="You are a senior data analyst.",
    instructions="Analyze the user input and provide a summary.",
    agent="agno",           # Choose engine: 'agno', 'langchain', 'crewai', 'pydantic_ai'
    model="gpt-4o-mini",    # Model ID
    config={"markdown": True}
)

# 2. Create the Agent
# Kibo handles the specific framework initialization under the hood
agent = create_agent(agent_def, api_key=os.getenv("OPENAI_API_KEY"))

# 3. Run it
result = agent.run("Compare Python vs Rust performance")
print(result.output_data)
```

### 3. Distributed & Parallel Workflow

One of Kibo's strongest features is running multiple heterogeneous agents in parallel via its distributed runtime.

```python
import asyncio
from kibo_core import AgentConfig, create_agent

async def main():
    # Define two different agents using different frameworks
    agent_a = create_agent(AgentConfig(
        name="Researcher", 
        agent="agno", 
        model="gpt-4o-mini",
        instructions="Research topic."
    ))
    
    agent_b = create_agent(AgentConfig(
        name="Writer", 
        agent="langchain", 
        model="gpt-4o-mini", 
        instructions="Write a poem."
    ))

    # Run them in parallel using async/await
    # Under the hood, this dispatches tasks to the generic Ray worker pool
    futures = [
        agent_a.run_async("Quantum Computing"),
        agent_b.run_async("The beauty of mathematics")
    ]
    
    # Wait for completion
    results = await asyncio.gather(*[asyncio.to_thread(f.result) for f in futures])
    
    for res in results:
        print(f"Result: {res.output_data[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📂 Project Structure

*   **`src/kibo_core/`**: The core framework source code.
    *   `application/`: Factory logic and workflow managers.
    *   `domain/`: Blueprints (`AgentConfig`) and entity definitions.
    *   `infrastructure/`: Adapters for different libraries (Agno, LangChain, etc.) and the Ray executor.
*   **`examples/`**: Simple scripts demonstrating how to use Kibo with specific frameworks (e.g., `agno_openai_example.py`, `crewai_example.py`).
*   **`use_case/`**: More complex, real-world scenarios.
    *   `finance_workflow.py`: Demonstrates a multi-agent pipeline combining research, summarization, and advice.

## 🚦 AI Gateway (Proxy)

Kibo includes a managed proxy to route LLM requests. This allows you to code against a generic OpenAI-compatible endpoint (`http://localhost:4000`) while the proxy handles routing to OpenAI, Anthropic, or local Ollama instances.

**To use it:**
1.  Add your keys to `.env` (e.g., `OPENAI_API_KEY=...`).
2.  Start the proxy: `uv run kibo proxy start`.
3.  Kibo agents will automatically detect the proxy if `KIBO_PROXY_URL` is set, or you can pass it explicitly in the agent config.

## 🤝 Contributing

This is an initial release of the Kibo Framework. We welcome contributions to add more adapters, improve the distributed scheduler, or enhance the gateway integration.

