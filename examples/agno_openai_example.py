import os
from kibo_core import AgentConfig, create_agent

def main():
    print("--- Agno (PhiData) + OpenAI + Kibo Blueprint Example ---")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    agent_def = AgentConfig(
        name='ScienceBot',
        description='You are a helpful science assistant.',
        instructions='Explain complex topics simply.',
        agent="agno",
        model="gpt-4o-mini",
        config={
            "markdown": True
        }
    )
    
    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching task...")
    try:
        result = agent.run("Explain Quantum Computing in 1 sentence.")
        
        print("\nResult:")
        print(result.output_data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
