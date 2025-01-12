import os
from kibo_core import AgentConfig, create_agent

def main():
    print("--- Kibo Blueprint Example (Zero-Dependency Definition) ---")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    # --- 1. Define Agent (Pure Data) ---
    my_agent_def = AgentConfig(
        name="AnalystBot",
        description="You are a senior data analyst with a sarcastic personality.",
        instructions="Analyze the user input and provide a summary with 3 bullet points.",
        agent="agno",
        model="gpt-4o-mini",
        config={"markdown": True}
    )

    # --- 2. Create Instance (Handles Kibo Internals) ---
    # Kibo handles the factory logic on the remote worker
    agent = create_agent(my_agent_def, api_key=api_key)

    print(f"Dispatching task to {my_agent_def.agent} engine...")
    try:
        # --- 3. Run ---
        result = agent.run("Comparison between Rust and Python performance.")
        
        print("\n--- Result ---")
        print(result.output_data)
        print(f"\nMetadata: {result.metadata}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
