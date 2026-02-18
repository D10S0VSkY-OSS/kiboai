# Getting Started

## Installation

Kibo is optimized for **uv**.

1.  **Clone:**
    ```bash
    git clone https://github.com/D10S0VSkY-OSS/kiboai.git
    cd kiboai
    ```

2.  **Install:**
    ```bash
    uv sync
    ```

## CLI Usage

Kibo comes with a CLI to manage the runtime.

```bash
# Start the runtime (Head node)
uv run kibo start --head

# Check status
uv run kibo status

# Start Proxy
uv run kibo proxy start
```

## Your First Agent

Create a file named `my_agent.py`:

```python
import os
from kiboai import AgentConfig, create_agent

# 1. Define
config = AgentConfig(
    name="MyBot",
    description="A helpful assistant",
    instructions="Answer nicely.",
    agent="agno",
    model="gpt-4o-mini"
)

# 2. Create
# Ensure OPENAI_API_KEY is in your environment
agent = create_agent(config, api_key=os.getenv("OPENAI_API_KEY"))

# 3. Run
print(agent.run("Hello Kibo!").output_data)
```

Run it:
```bash
uv run my_agent.py
```
