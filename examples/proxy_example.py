import os
from kibo_core import KiboAgent, AgentConfig

# -------------------------------------------------------------------------
# KIBO PROXY EXAMPLE
# -------------------------------------------------------------------------
# This example demonstrates how to use Kibo with its centralized Model Gateway.
# 
# Pre-requisites:
# 1. Start the proxy in a separate terminal:
#    $ kibo proxy start --model gpt-4o (or ollama/llama3, etc)
# 
# 2. Set your API Key if using OpenAI/Anthropic backing the proxy:
#    $ export OPENAI_API_KEY=sk-...
# -------------------------------------------------------------------------

# 1. Configure the Environment to use Kibo Proxy
# If this is set, Kibo factories will automatically route LLM requests to this URL.
os.environ["KIBO_PROXY_URL"] = "http://localhost:4000"

# 2. Define the Agent
# Note: We use "openai/..." prefix because the Proxy simulates an OpenAI-compatible API,
# effectively making any model (Ollama, Anthropic, Bedrock) look like OpenAI to the framework.
config = AgentConfig(
    name="proxy-demo-agent",
    description="You are a helpful AI assistant running behind a corporate proxy.",
    instructions="Answer concisely and professionally.",
    agent="crewai",  # We can swap this for 'agno' or 'langchain' without changing the proxy logic
)

def main():
    print(f"🚀 Connecting to Kibo Proxy at {os.environ['KIBO_PROXY_URL']}...")
    
    # 3. Initialize Client
    client = KiboAgent(config)

    # 4. Execute
    # The request goes: Client -> Framework (CrewAI) -> Kibo Proxy -> Real Provider (OpenAI/Ollama)
    try:
        query = "Explain what a reverse proxy is in one sentence."
        print(f"\nUser: {query}")
        
        result = client.run(query)
        
        print(f"\nAgent: {result}")
    except Exception as e:
        print(f"\n❌ Error: Could not connect to proxy. Did you run 'kibo proxy start'?")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
