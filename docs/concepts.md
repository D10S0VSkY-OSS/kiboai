# Core Concepts

## 1. The Blueprint (`AgentConfig`)

Kibo separates **definition** from **execution**. You define *what* an agent is using a pure data structure called a Blueprint (`AgentConfig`).

```python
@dataclass
class AgentConfig:
    name: str              # Unique ID
    description: str       # System Prompt / Backstory
    instructions: str      # Specific goal or task
    agent: str             # Engine: 'agno', 'langchain', 'crewai', etc.
    model: str             # Model ID (e.g., 'gpt-4o', 'ollama/llama3')
    config: dict = None    # Extra params (tools, verbose, etc.)
```

This makes your agents portable. You can store these configs in a database, JSON file, or YAML, and hydrate them into live agents at runtime.

## 2. Adapters

Kibo uses the **Adapter Pattern** to wrap different underlying libraries.

*   **`AgnoAdapter`**: Wraps Agno (formerly PhiData) agents.
*   **`LangChainAdapter`**: Wraps LangChain chains/agents.
*   **`CrewAIAdapter`**: Wraps CrewAI Crews (Agent + Task).
*   **`PydanticAIAdapter`**: Wraps PydanticAI Agents.

You interact with the uniform `IAgentNode` interface (`execute`, `aexecute`), and Kibo handles the framework-specific API calls internally.

## 3. Distributed Runtime (Ray)

When you call `create_distributed_agent` or run a workflow, Kibo leverages **Ray**.

*   **Isolation**: Each agent can run in its own process or actor.
*   **Parallelism**: Run 100 agents simultaneously without blocking your main loop.
*   **Scaling**: Deploy Kibo on a cluster of machines.

## 4. AI Gateway (Proxy)

Kibo integrates **LiteLLM** to act as a centralized gateway.

*   **One API**: Your agents talk to `http://localhost:4000`.
*   **Routing**: The gateway routes to OpenAI, Anthropic, Gemini, or local Ollama.
*   **Control**: logging, caching, and rate limiting happens at the gateway level.
