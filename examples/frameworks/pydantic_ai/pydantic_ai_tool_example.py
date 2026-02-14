import os
import sys
import random

# Ensure Kibo is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core import AgentConfig, create_agent


# 1. Define Native Python Function as Tool
# PydanticAI accepts plain functions type-hinted correctly
def roll_die(sides: int = 6) -> str:
    """
    Rolls a die with the given number of sides.

    Args:
        sides: Number of sides on the die (default 6).
    """
    if sides < 2:
        return "A die must have at least 2 sides."
    result = random.randint(1, sides)
    return f"Rolled a {result} (d{sides})"


def main():
    print("--- PydanticAI Agent with Native Tool (Function) ---")

    # 2. Configure Agent
    config = AgentConfig(
        name="GameMaster",
        description="A dungeon master helper.",
        instructions="Roll a d20 and a d6, then describe the outcome of an attack.",
        agent="pydantic_ai",
        config={"tools": [roll_die]},  # Pass the function directly
    )

    # 3. Create & Run
    agent = create_agent(config, api_key="sk-dummy")

    try:
        result = agent.run("Attack the goblin!")
        print("\n--- Result ---")
        print(result.output_data)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
