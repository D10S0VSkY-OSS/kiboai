import os
import json
import time
import requests
from kibo_core import KiboAgent, AgentConfig

# -------------------------------------------------------------------------
# KIBO PROXY: ADVANCED FEATURES (Quotas, Budgets, Cost Tracking)
# -------------------------------------------------------------------------
# This example demonstrates how to control costs and budgets using the Kibo Proxy
# with a YAML configuration file and Virtual Keys.
# 
# Pre-requisites:
# 1. The config file 'examples/proxy_config.yaml' is already provided.
# 2. Start the proxy with this config:
#    $ export OPENAI_API_KEY=sk-....
#    $ kibo proxy start --config examples/proxy_config.yaml
# -------------------------------------------------------------------------

# NOTE: Virtual Keys with defined Budgets require a persistent Database (Redis/Postgres).
# Since this example runs locally without a DB, we use a random key (Proxy is open).
# We still get Rate Limiting (RPM/TPM) which works in-memory.

VIRTUAL_KEY = "sk-any-random-key" 
# ADMIN_KEY = "sk-admin-master"

def run_agent_with_budget():
    print(f"\n🚀 Acting as User using Key: {VIRTUAL_KEY}")
    print("   (Note: Persistent Budget tracking disabled because no DB is connected)")
    
    # 1. Point to Kibo Proxy
    os.environ["KIBO_PROXY_URL"] = "http://localhost:4000"
    
    # 2. Use the KEY
    agent_config = AgentConfig(
        name="budget-agent",
        description="Cost-conscious assistant.",
        instructions="Say hello and tell me a very short joke about money.",
        framework="crewai",
        model="openai/gpt-4o-mini"
    )

    try:
        # Override Key for this run
        os.environ["OPENAI_API_KEY"] = VIRTUAL_KEY
        
        agent = KiboAgent(agent_config)
        result = agent.run("Do your job.")
        print(f"\n🤖 Agent Reply: {result.output_data}")
        
        # 3. Check Request Cost (Stateless)
        # We can inspect the metadata returned by Kibo to see usage
        print("\n💰 Request Cost Analysis (Stateless):")
        meta = result.metadata
        usage = meta.get("token_usage", {})
        print(f"   -> Model: {meta.get('model')}")
        print(f"   -> Usage: {usage}")
        
        # Calculate approximate cost if not provided directly (gpt-4o-mini rates)
        # Input: $0.15 / 1M tokens, Output: $0.60 / 1M tokens
        if hasattr(usage, 'prompt_tokens') and hasattr(usage, 'completion_tokens'):
             cost = (usage.prompt_tokens * 0.15 + usage.completion_tokens * 0.60) / 1_000_000
             print(f"   -> Approx Cost: ${cost:.6f}")

    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        return

if __name__ == "__main__":

    
    if not os.environ.get("OPENAI_API_KEY"):
        # Just a friendly warning, though strictly the python client script doesn't need it,
        # only the proxy needs it. But the script simulates client env.
        pass
    
    run_agent_with_budget()
