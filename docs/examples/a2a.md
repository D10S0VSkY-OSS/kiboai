# Agent-to-Agent (A2A) Examples

This section demonstrates how to create agents that communicate with each other using the Agent-to-Agent (A2A) protocol.

## A2A Client Example
Location: `examples/a2a/client_example.py`

This example shows how to implement an agent that acts as a client, sending requests to another agent.

```python
import os

from kibo_core import AgentConfig, A2AConfig, create_agent
from kibo_core.shared_kernel.logging import logger


def main():
    logger.info("--- Kibo A2A Client Example (Agno) ---")

    host = os.getenv("KIBO_A2A_HOST", "localhost")
    port = int(os.getenv("KIBO_A2A_PORT", "7777"))
    agent_id = os.getenv("KIBO_A2A_AGENT_ID", "server-bot")
    query = "Hello Server! What is 2 + 2?"
    logger.info("Sending Query: '%s'", query)

    agent_def = AgentConfig(
        name="ClientBot",
        description="I am a client agent.",
        instructions="Delegate to remote.",
        agent="agno",
        model="gpt-4o-mini",
        a2a=A2AConfig(
            mode="client",
            host=host,
            port=port,
            agent_id=agent_id,
        ),
    )

    client_agent = create_agent(agent_def)

    try:
        result = client_agent.run(query)
        logger.info("Response: %s", result.output_data)
        logger.info("Metadata: %s", result.metadata)
    except Exception as e:
        logger.error("Error: %s", e)
        logger.error("Ensure the server_example.py is running in another terminal.")


if __name__ == "__main__":
    main()
```

```bash
uv run examples/a2a/client_example.py
```

## A2A Server Example
Location: `examples/a2a/server_example.py`

This example demonstrates how to implement an agent that acts as a server, receiving requests from other agents and responding.

```python
import os

from kibo_core import AgentConfig, A2AConfig, create_agent
from kibo_core.shared_kernel.logging import logger


def main():
    logger.info("--- Kibo A2A Server Example (Agno) ---")

    host = os.getenv("KIBO_A2A_HOST", "localhost")
    port = int(os.getenv("KIBO_A2A_PORT", "7777"))
    agent_id = os.getenv("KIBO_A2A_AGENT_ID", "server-bot")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is required for Agno A2A server.")
        return

    agent_def = AgentConfig(
        name="ServerBot",
        description="A helpful assistant running as a server.",
        instructions="You are a server-side agent. Answer short and concise.",
        agent="agno",
        model="gpt-4o-mini",
        a2a=A2AConfig(
            mode="server",
            host=host,
            port=port,
            agent_id=agent_id,
            access_log=True,
        ),
    )

    logger.info("Creating agent '%s'...", agent_def.name)
    server_agent = create_agent(agent_def, api_key=api_key)

    logger.info("Starting A2A server on http://%s:%s", host, port)
    logger.info("Agent endpoint: /a2a/agents/%s/v1/message:send", agent_id)

    server_agent.run("START_SERVER")


if __name__ == "__main__":
    main()
```

```bash
uv run examples/a2a/server_example.py
```
