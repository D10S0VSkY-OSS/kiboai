import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from kiboai import AgentConfig, create_agent
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    expression: str = Field(
        ..., description="The mathematical expression to evaluate (e.g., '2 + 2')"
    )


class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "A useful tool for calculating mathematical expressions."
    args_schema: type[BaseModel] = CalculatorInput

    def _run(self, expression: str) -> str:
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {e}"


calc_tool = CalculatorTool()


def main():
    print("--- CrewAI Agent with Native Tool (Custom Calculator) ---")

    config = AgentConfig(
        name="MathProfessor",
        description="A professor who excels at math.",
        instructions="Calculate 123 * 456 and explain the result simply.",
        agent="crewai",
        config={"verbose": True, "tools": [calc_tool]},  # Pass CrewAI BaseTool directly
    )

    agent = create_agent(config, api_key="sk-dummy")

    try:
        result = agent.run("What is 123 * 456?")
        print("\n--- Result ---")
        print(result.output_data)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
