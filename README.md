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

## 📂 Project Structure

*   **`src/kibo_core/`**: Core framework.
    *   `infrastructure/adapters/`: Logic to wrap specific frameworks.
    *   `infrastructure/executors/`: Ray and Local executors.
*   **`examples/`**:
    *   `agno_tool_example.py`: Using Agno tools (YFinance).
    *   `langchain_tool_example.py`: Using Google Serper with LangChain.
    *   `crewai_prebuilt_tool_example.py`: Using native tools with CrewAI.
    *   `parallel_execution_example.py`: Distributed execution demo.

## 🤝 Contributing

We welcome contributions to add more adapters or improve the runtime!
