# Welcome to Kibo AI

**The Universal Distributed Agent Framework**

Kibo is a powerful abstraction framework designed to unify the orchestration of AI Agents. It allows developers to define, execute, and combine agents from different underlying libraries (like **Agno**, **LangChain**, **CrewAI**, and **PydanticAI**) within a single, consistent interface.

!!! tip "Why Kibo?"
    Kibo goes beyond simple wrapping; it enables **distributed** and **parallel** execution of agents via Ray, allowing you to build complex, high-performance AI workflows that scale.

## 🚀 Key Features

*   **Unified Abstraction**: Define agents using a generic `AgentConfig`.
*   **Multi-Framework Support**: Mix and match Agno, LangChain, CrewAI, PydanticAI, and LangGraph.
*   **Distributed Runtime**: Built on top of **Ray** for robust parallel execution.
*   **Integrated Gateway**: Unified model access via LiteLLM.
*   **Zero-Dependency Definitions**: Pure Python data structures for agent blueprints.

## 📦 Quick Install

```bash
git clone https://github.com/D10S0VSkY-OSS/kiboai.git
cd kiboai
uv sync
```

[Get Started](getting-started.md){ .md-button .md-button--primary }
