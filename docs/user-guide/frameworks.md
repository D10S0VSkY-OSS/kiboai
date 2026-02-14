# Framework Integrations

Kibo is designed to support the ecosystem, not replace it. Here is how to configure agents for each supported backend, including Native Tool integration.

## Agno (PhiData)

Best for general-purpose assistants and tool calling.

```python
from agno.tools.yfinance import YFinanceTools

config = AgentConfig(
    agent="agno",
    model="gpt-4o-mini",
    config={
        "markdown": True,
        "show_tool_calls": False,
        "tools": [YFinanceTools()] # Pass native Agno tools
    }
)
```

## LangChain

Uses `ChatOpenAI` and generic prompt templates. Supports `langchain_core.tools` and community tools.

```python
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool

search = GoogleSerperAPIWrapper()
tool = Tool(name="Search", func=search.run, description="Search Google")

config = AgentConfig(
    agent="langchain",
    model="gpt-4o-mini",
    config={
        "tools": [tool] # Pass native LangChain tools
    }
)
```

## CrewAI

Creates a single-agent Crew (Agent + Task) for process-oriented workflows.

```python
from crewai.tools import BaseTool

class MyTool(BaseTool):
    name: str = "MyTool"
    description: str = "Does something."
    def _run(self, arg): return "done"

config = AgentConfig(
    agent="crewai",
    model="gpt-4o-mini",
    config={
        "verbose": True,
        "tools": [MyTool()] # Pass native CrewAI tools
    }
)
```

## PydanticAI

Uses PydanticAI's type-safe agent structure. Supports standard Python functions as tools.

```python
def my_tool(x: int) -> int:
    """Returns double x."""
    return x * 2

config = AgentConfig(
    agent="pydantic-ai",
    model="gpt-4o-mini",
    config={
        "tools": [my_tool] # Pass python functions directly
    }
)
```

## LangGraph

Deploys a pre-compiled state graph.

```python
config = AgentConfig(
    agent="langgraph",
    model="gpt-4o-mini"
)
```
