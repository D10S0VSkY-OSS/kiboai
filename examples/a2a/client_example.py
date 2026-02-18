import os

from kiboai import AgentConfig, A2AConfig, create_agent
from kiboai.shared_kernel.logging import logger


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
