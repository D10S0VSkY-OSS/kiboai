# Framework Integration Examples

Kibo unifies multiple AI frameworks under a single API. Here are examples of using Kibo with various underlying engines.

## Agno (formerly PhiData)
Location: `examples/frameworks/agno/`

*   **Gemini Integration**: `agno_native_gemini_example.py` - Using Google Gemini models.
*   **OpenAI Integration**: `agno_openai_example.py` - Using OpenAI models.
*   **Tool Usage**: `agno_tool_example.py` - Demonstrating native tool integration (e.g., YFinance).

```bash
uv run examples/frameworks/agno/agno_native_gemini_example.py
```

## CrewAI
Location: `examples/frameworks/crewai/`

*   **Basic Agent**: `crewai_example.py`
*   **Gemini/OpenAI**: Specific vendor implementations.
*   **Tool Usage**: `crewai_tool_example.py` - Using tools within a Kibo-wrapped CrewAI agent.

## LangChain
Location: `examples/frameworks/langchain/`

*   **Basic Agent**: `langchain_example.py`
*   **Tool Usage**: `langchain_tool_example.py`
*   **Vendor Integrations**: OpenAI and Gemini examples.

## LangGraph
Location: `examples/frameworks/langgraph/`

Examples showing how Kibo can orchestrate LangGraph-based flows.

## PydanticAI
Location: `examples/frameworks/pydantic_ai/`

Demonstrating the integration with PydanticAI for type-safe agent interactions.
