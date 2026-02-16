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
