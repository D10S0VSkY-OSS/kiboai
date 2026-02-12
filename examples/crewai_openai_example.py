import sys
import os
from kibo_core import AgentConfig, create_agent

def main():
    print("--- CrewAI + OpenAI + Kibo Blueprint Example ---")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    agent_def = AgentConfig(
        name='Economist',
        description='You are an expert in budget optimization.',
        instructions='Analyze cost-effective AI strategies.',
        agent="crewai",
        model="gpt-4o-mini",
        config={
            "verbose": True,
            "allow_delegation": False
        }
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching Crew to Kibo Cluster...")
    try:
        input_data = "saving money on LLM API usage" 
        
        task = agent.run_async(input_data)
        result = task.result()
        
        print("\n--- Result ---")
        print(result.output_data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
