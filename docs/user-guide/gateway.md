# AI Gateway (Managed Proxy)

Kibo ships with a built-in proxy server based on **LiteLLM**. This provides a compatibility layer between your agents and various LLM providers.

## Why use it?
1.  **Uniform API**: Your agents always talk to `openai`-compatible endpoints.
2.  **Cost Tracking**: The proxy logs token usage and costs.
3.  **Failover**: Configure fallback models (e.g., if OpenAI is down, try Anthropic).
4.  **Security**: Keep your real API keys in the proxy config, giving agents only the proxy URL.

## Configuration

The proxy is configured via `proxy_config.yaml`.

```yaml
model_list:
  - model_name: gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  - model_name: llama3
    litellm_params:
      model: ollama/llama3
      api_base: http://localhost:11434
```

## Running the Proxy

```bash
uv run kibo proxy start --config examples/proxy_config.yaml
```

The proxy starts on port `4000` (default).

## Connecting Agents

If you set the `KIBO_PROXY_URL` environment variable, Kibo agents automatically route traffic through it.

```bash
export KIBO_PROXY_URL="http://localhost:4000"
# Now run your agents
uv run examples/blueprint_example.py
```
