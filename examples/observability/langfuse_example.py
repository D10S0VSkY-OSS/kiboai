import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from kiboai import AgentConfig, LangfuseConfig, create_agent
from kiboai.shared_kernel.logging import logger


def main():
    load_dotenv()
    logger.info("--- Kibo Langfuse Example ---")

    agent_def = AgentConfig(
        name="LangfuseBot",
        description="A helpful assistant with tracing.",
        instructions="Answer short and concise.",
        agent="agno",
        model="gpt-4o-mini",
        langfuse=LangfuseConfig(
            enabled=True,
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            trace_name="kibo.langfuse_example",
        ),
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is required to run this example.")
        return

    agent = create_agent(agent_def, api_key=api_key)
    result = agent.run("Hello from Kibo with Langfuse")

    logger.info("Response: %s", result.output_data)
    logger.info("Metadata: %s", result.metadata)


if __name__ == "__main__":
    main()
