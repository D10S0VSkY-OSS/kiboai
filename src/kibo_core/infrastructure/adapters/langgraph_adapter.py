from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult


class LangGraphAdapter(IAgentNode):
    """
    Adapter for LangGraph Compiled Graphs.
    """

    def __init__(self, graph):
        self.graph = graph

    def execute(self, request: AgentRequest) -> AgentResult:
        inputs = request.input_data

        # Ensure inputs is a dict if it's not already
        if not isinstance(inputs, dict):
            # Try to infer if it's a simple message content
            if isinstance(inputs, str):
                inputs = {"messages": [("user", inputs)]}
            elif hasattr(inputs, "content"):
                inputs = {"messages": [inputs]}
            else:
                # Fallback
                inputs = {"messages": [("user", str(inputs))]}

        # Extract config from context params if available
        config = {}
        if request.context and request.context.params:
            # Merge all params as config? Or extract 'config' key?
            # LangGraph invoke expects 'config' as second argument.
            # Let's assume params contains the whole config dict or keys like 'configurable'
            # If user passed params={"configurable": {"thread_id": "1"}}, we can pass params directly as config
            config = request.context.params

        result = self.graph.invoke(inputs, config=config)

        output = "No output found"
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                last_msg = messages[-1]
                output = getattr(last_msg, "content", str(last_msg))
        else:
            output = str(result)

        return AgentResult(output_data=output, metadata={"adapter": "LangGraphAdapter"})

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        inputs = request.input_data

        # Ensure inputs is a dict if it's not already
        if not isinstance(inputs, dict):
            # Try to infer if it's a simple message content
            if isinstance(inputs, str):
                inputs = {"messages": [("user", inputs)]}
            elif hasattr(inputs, "content"):
                inputs = {"messages": [inputs]}
            else:
                # Fallback
                inputs = {"messages": [("user", str(inputs))]}

        # Extract config from context params if available
        config = {}
        if request.context and request.context.params:
            config = request.context.params

        result = await self.graph.ainvoke(inputs, config=config)

        output = "No output found"
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                last_msg = messages[-1]
                output = getattr(last_msg, "content", str(last_msg))
        else:
            output = str(result)

        return AgentResult(output_data=output, metadata={"adapter": "LangGraphAdapter"})
