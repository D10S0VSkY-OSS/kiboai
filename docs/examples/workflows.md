# Complex Workflow: Finance Analyst

This use case demonstrates a real-world scenario: **Financial Market Analysis**.

It combines:
1.  **Multiple Frameworks**: Agno, LangChain, CrewAI, and PydanticAI working together.
2.  **Tool Use**: Agents equipped with search tools (Tavily).
3.  **Parallelism**: Fetching Gold, Crypto, and Stock data simultaneously.
4.  **Synthesis**: A final advisor agent that aggregates all reports into a conclusion.
5.  **Cost Calculation**: Tracking the cost of execution.

`use_case/finance_workflow.py`

```python
--8<-- "use_case/finance_workflow.py"
```
