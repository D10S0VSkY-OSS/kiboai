# AI Gateway (Proxy)

Kibo includes a built-in AI Gateway (powered by LiteLLM) to manage model access, API keys, and routing.

## Basic Usage
Location: `examples/proxy/proxy_example.py`

Start the proxy and route simple requests.

```python
import os
from kibo_core import KiboAgent, AgentConfig

os.environ["KIBO_PROXY_URL"] = "http://localhost:4000"

config = AgentConfig(
    name="proxy-demo-agent",
    description="You are a helpful AI assistant running behind a corporate proxy.",
    instructions="Answer concisely and professionally.",
    agent="crewai",  # We can swap this for 'agno' or 'langchain' without changing the proxy logic
)


def main():
    print(f" Connecting to Kibo Proxy at {os.environ['KIBO_PROXY_URL']}...")

    client = KiboAgent(config)

    try:
        query = "Explain what a reverse proxy is in one sentence."
        print(f"\nUser: {query}")

        result = client.run(query)

        print(f"\nAgent: {result}")
    except Exception as e:
        print(f"\n Error: Could not connect to proxy. Did you run 'kibo proxy start'?")
        print(f"Details: {e}")


if __name__ == "__main__":
    main()
```


## Advanced Configuration
Location: `examples/proxy/proxy_advanced_example.py`
Config: `examples/proxy/proxy_config.yaml`

Shows how to configure the proxy with custom routing rules, load balancing, or fallback strategies.

```bash
# Start the proxy
uv run kibo proxy start
```
