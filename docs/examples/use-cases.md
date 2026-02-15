# Real-World Use Cases

Practical applications demonstrating the power of the Kibo framework.

## 📈 Finance Workflow
Location: `examples/use_case/finance_workflow.py`

A comprehensive multi-agent system for financial analysis. This example demonstrates:
*   **Parallel Execution**: Fetching data for Stocks, Crypto, and Commodities simultaneously.
*   **Tool Usage**: Agents equipped with search and finance tools (e.g., YFinance, Tavily).
*   **Synthesis**: A final "Head Analyst" agent that aggregates reports from specialized workers into a cohesive investment recommendation.
*   **Multi-Framework**: Orchestrating agents that might be powered by different underlying engines.

```bash
uv run examples/use_case/finance_workflow.py
```

## 🧠 Memory Chat (RAG)
Location: `examples/use_case/memory_chat_example.py`

A stateful chat application that remembers user interactions and context. This example showcases Kibo's usage of:
*   **Vector Database**: Storing conversation history in ChromaDB.
*   **Memory Management**: Retrieving relevant past context (RAG - Retrieval Augmented Generation) to answer current queries.
*   **Persistence**: Maintaining user state across sessions.

**Prerequisites:**
Ensure the ChromaDB service is running:
```bash
uv run kibo start db
```

**Run the example:**
```bash
uv run examples/use_case/memory_chat_example.py
```
