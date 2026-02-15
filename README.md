# Kibo AI Framework

**Kibo** is a powerful and flexible abstraction framework designed to unify the orchestration of AI Agents. It allows developers to define, execute, and combine agents from different underlying libraries (like **Agno**, **LangChain**, **CrewAI**, and **PydanticAI**) within a single, consistent interface.

Kibo goes beyond simple wrapping; it enables **distributed** and **parallel** execution of agents, allowing you to build complex, high-performance AI workflows that scale across multiple nodes or naturally on a single machine. It includes a unified **Native Tooling** system and a built-in **AI Gateway**.

## 🚀 Key Features

*   **Unified Abstraction**: Define agents using a generic `AgentConfig` blueprint. Switch the underlying engine (e.g., from `agno` to `langchain`) just by changing a string configuration.
*   **Multi-Framework Support**: Seamlessly mix and match agents:
    *   **Agno (PhiData)**
    *   **LangChain**
    *   **CrewAI**
    *   **PydanticAI**
    *   **LangGraph**
*   **Dual Runtime Mode**:
    *   **Local Mode**: Run agents via thread pools for simple, low-overhead concurrency.
    *   **Distributed Mode**: Scale up using **Ray** as the execution backend for heavy workloads across clusters.
*   **Native Tool Integration**: Pass native tools (like `LangChain Tools`, `Agno Toolkits`, or standard Python functions) directly to Kibo agents. The framework automatically adapts them if necessary.
*   **Zero-Dependency Definitions**: Define agent behaviors in pure Python data structures (Blueprints).

## 📦 Installation

Kibo is optimized for use with **uv** for fast and reliable dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/D10S0VSkY-OSS/kiboai.git
    cd kiboai
    ```

2.  **Install dependencies using uv:**
    ```bash
    uv sync
    ```

## 🛠️ Usage

### 1. Creating an Agent with Native Tools

Kibo allows you to inject native tools directly into the configuration.

**Agno Example (YFinance):**
```python
from kibo_core import AgentConfig, create_agent
from agno.tools.yfinance import YFinanceTools

# 1. Initialize the native tool
tool = YFinanceTools()

# 2. Configure Agent
config = AgentConfig(
    name="StockBot",
    description="Financial Analyst",
    instructions="Get stock prices.",
    agent="agno",
    config={
        "tools": [tool]  # Pass native tool directly
    }
)

# 3. Run
agent = create_agent(config, api_key="...")
print(agent.run("Price of Apple?").output_data)
```

### 2. Distributed vs. Local Execution

By default, agents effectively run in **Local Mode**. To enable **Distributed Mode** (using Ray), simply set the flag in the configuration or factory.

```python
# Enable Distributed Mode in Config
agent_def = AgentConfig(
    name="HeavyWorker", 
    agent="crewai", 
    instructions="Do hard work.",
    distributed=True  # <--- Activates Ray Runtime
)

agent = create_agent(agent_def)
# The generic 'run_async' will now dispatch to the Ray Cluster
future = agent.run_async("Start processing")
```

### 3. The Kibo CLI
Manage the runtime environment and Gateway.

```bash
# Start the Kibo distributed runtime (Head node)
uv run kibo start --head

# Use the Proxy
uv run kibo proxy start
```

## � Examples Inventory

Explore the `examples/` directory to see Kibo in action. Run any example using `uv run path/to/example.py`.

### 🏗️ Frameworks
Demonstrates how to use different underlying agent engines with Kibo's unified API.

#### Agno (formerly PhiData)
*   **Gemini Integration**: `examples/frameworks/agno/agno_native_gemini_example.py`
*   **OpenAI Integration**: `examples/frameworks/agno/agno_openai_example.py`
*   **Tool Usage**: `examples/frameworks/agno/agno_tool_example.py`

#### CrewAI
*   **Basic Agent**: `examples/frameworks/crewai/crewai_example.py`
*   **Gemini Integration**: `examples/frameworks/crewai/crewai_native_gemini_example.py`
*   **OpenAI Integration**: `examples/frameworks/crewai/crewai_openai_example.py`
*   **Tool Usage**: `examples/frameworks/crewai/crewai_tool_example.py`

#### LangChain
*   **Basic Agent**: `examples/frameworks/langchain/langchain_example.py`
*   **Gemini Integration**: `examples/frameworks/langchain/langchain_native_gemini_example.py`
*   **OpenAI Integration**: `examples/frameworks/langchain/langchain_openai_example.py`
*   **Tool Usage**: `examples/frameworks/langchain/langchain_tool_example.py`

#### LangGraph
*   **Gemini Integration**: `examples/frameworks/langgraph/langgraph_native_gemini_example.py`
*   **OpenAI Integration**: `examples/frameworks/langgraph/langgraph_openai_example.py`

#### PydanticAI
*   **Gemini Integration**: `examples/frameworks/pydantic_ai/pydantic_ai_native_gemini_example.py`
*   **OpenAI Integration**: `examples/frameworks/pydantic_ai/pydantic_ai_openai_example.py`
*   **Tool Usage**: `examples/frameworks/pydantic_ai/pydantic_ai_tool_example.py`

### 🔄 Workflows
Orchestrate complex sequences of tasks.

*   **Agno Workflow**: `examples/workflows/agno_workflow_example.py`
*   **Translation Workflow (Agno)**: `examples/workflows/agno_workflow_translation.py`
*   **Declarative Workflow (YAML-style)**: `examples/workflows/declarative_workflow_example.py`
*   **CrewAI Declarative**: `examples/workflows/crewai_declarative_example.py`
*   **Native Extensions**: `examples/workflows/native_extensions_example.py`
*   **Workflow with Gemini**: `examples/workflows/workflow_native_gemini_example.py`

### ⚡ Distributed & Parallel
Scale your agents using the Ray runtime.

*   **Parallel Execution**: `examples/distributed/parallel_execution_example.py`
*   **Declarative Distributed**: `examples/distributed/distributed_declarative_example.py`
*   **Imperative Distributed**: `examples/distributed/distributed_imperative_example.py`

### 🛡️ Proxy & Gateway
Use the built-in AI Gateway for model routing and key management.

*   **Basic Proxy Usage**: `examples/proxy/proxy_example.py`
*   **Advanced Proxy Config**: `examples/proxy/proxy_advanced_example.py`

### 💡 Use Cases
Real-world application scenarios.

*   **Finance Workflow**: `examples/use_case/finance_workflow.py`
*   **Memory Chat**: `examples/use_case/memory_chat_example.py`

### 🟢 Basics
Getting started with core concepts.

*   **Blueprint Basics**: `examples/basics/blueprint_example.py`

## 🤝 Contributing

We welcome contributions to add more adapters or improve the runtime!
