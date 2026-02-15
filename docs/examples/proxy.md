# AI Gateway (Proxy)

Kibo includes a built-in AI Gateway (powered by LiteLLM) to manage model access, API keys, and routing.

## Basic Usage
Location: `examples/proxy/proxy_example.py`

Start the proxy and route simple requests.

## Advanced Configuration
Location: `examples/proxy/proxy_advanced_example.py`
Config: `examples/proxy/proxy_config.yaml`

Shows how to configure the proxy with custom routing rules, load balancing, or fallback strategies.

```bash
# Start the proxy
uv run kibo proxy start
```
