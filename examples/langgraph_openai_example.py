import os
from kibo_core import AgentConfig, create_agent
from langchain_core.messages import HumanMessage

def main():
    print("--- LangGraph + OpenAI + Kibo Blueprint Example ---")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    agent_def = AgentConfig(
        name='PoetBot',
        description='A poet specialized in tech haikus.',
        instructions='Write a haiku about {topic}.',
        agent="langgraph",
        model="gpt-4o-mini"
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching task...")
    try:
        input_data = {"messages": [HumanMessage(content="Write a haiku about distributed systems.")]}
        
        result = agent.run(input_data)
        
        print("\nResult:")
        print(result.output_data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
