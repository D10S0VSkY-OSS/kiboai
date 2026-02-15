# Workflow Examples

Kibo supports orchestrating complex sequences of tasks, allowing you to chain agents together.

## Declarative Workflows (YAML-style)
Location: `examples/workflows/declarative_workflow_example.py`

Define your entire multi-step process in a simple configuration object (or YAML file). This example shows how to chain a research agent into a writer agent.

```bash
uv run examples/workflows/declarative_workflow_example.py
```

## Native Tool Integration
Location: `examples/workflows/workflow_native_gemini_example.py`

Execute workflows using Gemini models with native function calling capabilities.

```bash
uv run examples/workflows/workflow_native_gemini_example.py
```

## Framework-Specific Workflows

### Agno (PhiData)
*   **Standard Workflow**: `examples/workflows/agno_workflow_example.py` - Basic chaining of Agno agents.
*   **Translation Workflow**: `examples/workflows/agno_workflow_translation.py` - A pipeline for translating content.

### CrewAI
*   **Declarative Config**: `examples/workflows/crewai_declarative_example.py` - Configuring a CrewAI process using Kibo's declarative syntax.

## Native Extensions
Location: `examples/workflows/native_extensions_example.py`

Demonstrates how to pass low-level configuration options (like specific graph state definitions or CrewAI process overrides) to the underlying engine while still using Kibo's high-level API.

```bash
uv run examples/workflows/native_extensions_example.py
```
