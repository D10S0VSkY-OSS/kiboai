import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kiboai import AgentConfig, create_agent


def main():
    print("Example 1: Distributed Execution via Configuration (Declarative)")

    # Define Agent Config with distributed=True
    config = AgentConfig(
        name="ClusterAgent",
        description="An agent configured to always run on the cluster.",
        instructions="Return a greeting identifying your execution environment.",
        agent="mock",  # Use Mock agent for simplicity
        distributed=True,  # <--- KEY CONFIGURATION
        config={"echo_prefix": "Cluster Config Says: "},
    )

    # Create Agent (will connect to Ray automatically)
    agent = create_agent(config, api_key="sk-dummy")

    print("Dispatching task...")
    try:
        result = agent.run("Hello Kibo!")
        print(f"Result: {result.output_data}")
        print(f"Metadata: {result.metadata}")
    except Exception as e:
        print(f"Execution failed: {e}")


if __name__ == "__main__":
    main()
