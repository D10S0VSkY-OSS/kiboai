# Basic Usage

This guide covers how to create simple agents using the Kibo SDK.

## Defining an Agent

The `AgentConfig` acts as the DNA of your agent.

```python
from kibo_core import AgentConfig

agent_def = AgentConfig(
    name="MathTutor",
    description="You are a patient math tutor.",
    instructions="Explain the solution step-by-step.",
    agent="agno",
    model="gpt-4o-mini"
)
```

## Creating the Instance

Use the `create_agent` factory. This function detects the requested engine (`agno`, `langchain`, etc.) and returns the appropriate adapter.

```python
from kibo_core import create_agent

agent = create_agent(agent_def, api_key="sk-...")
```

## Running an Agent

All Kibo agents expose a synchronous `run` method and an asynchronous `run_async` method.

### Synchronous
```python
result = agent.run("What is the square root of 144?")
print(result.output_data)  # "The square root of 144 is 12."
print(result.metadata)     # Contains usage info, adapter name, etc.
```

### Asynchronous
```python
import asyncio

async def main():
    result = agent.run_async("What is pi?") # Returns a KiboFuture
    # To wait for the result:
    final = result.result() # Blocking call on the future
    # OR in a truly async loop (with asyncio.to_thread wrapping)
    # See Distributed Execution section for best practices.
```
