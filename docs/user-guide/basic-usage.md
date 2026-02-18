# Basic Usage

This guide covers how to create simple agents and use native tools.

## Defining an Agent

The `AgentConfig` acts as the DNA of your agent.

```python
from kiboai import AgentConfig

agent_def = AgentConfig(
    name="MathTutor",
    description="You are a patient math tutor.",
    instructions="Explain the solution step-by-step.",
    agent="agno",      # 'agno', 'langchain', 'crewai', 'pydantic_ai'
    model="gpt-4o-mini"
)
```

## Using Native Tools

Kibo provides first-class support for the native tool ecosystems of underlying frameworks. You can instantiate a tool from a library (like `langchain_community` or `agno.tools`) and pass it directly to the `config` dictionary.

### Example: Using Agno YFinance Tool
```python
from kiboai import create_agent, AgentConfig
from agno.tools.yfinance import YFinanceTools

# Instantiate the native tool
tool = YFinanceTools()

config = AgentConfig(
    name="FinanceBot",
    description="Analyst",
    instructions="Check stock prices.",
    agent="agno",
    config={
        "tools": [tool] # Pass it directly in the list
    }
)

agent = create_agent(config, api_key="sk-...")
agent.run("AAPL price")
```

### Example: Using Custom Python Functions (PydanticAI)
For frameworks like PydanticAI, you can simply pass python functions.

```python
import random

def roll_die(sides: int = 6) -> str:
    return str(random.randint(1, sides))

config = AgentConfig(
    name="GameMaster",
    description="DM",
    instructions="Roll dice.",
    agent="pydantic_ai",
    config={
        "tools": [roll_die]
    }
)
```

## Running an Agent

All Kibo agents expose a synchronous `run` method and an asynchronous `run_async` method.

### Synchronous
```python
result = agent.run("What is the square root of 144?")
print(result.output_data)  # "The square root of 144 is 12."
print(result.metadata)     # Contains usage info, adapter name, etc.
```

### Asynchronous (Future-based)
```python
future = agent.run_async("What is pi?") 
# Do other work...
result = future.result() # Blocks until completion
```
