# Framework Integrations

Kibo is designed to support the ecosystem, not replace it. Here is how to configure agents for each supported backend.

## Agno (PhiData)

Best for general-purpose assistants and tool calling.

```python
config = AgentConfig(
    agent="agno",
    model="gpt-4o-mini",
    config={
        "markdown": True,
        "tools": [] # Add tool instances here if constructing programmatically
    }
)
```

## LangChain

Uses `ChatOpenAI` and generic prompt templates.

```python
config = AgentConfig(
    agent="langchain",
    model="gpt-4o-mini",
    instructions="Process this text..."
)
```

## CrewAI

Creates a single-agent Crew (Agent + Task) for process-oriented workflows.

```python
config = AgentConfig(
    agent="crewai",
    model="gpt-4o-mini",
    config={
        "verbose": True,
        "allow_delegation": False
    }
)
```

## PydanticAI

Uses PydanticAI's type-safe agent structure.

```python
config = AgentConfig(
    agent="pydantic-ai",
    model="gpt-4o-mini"
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
