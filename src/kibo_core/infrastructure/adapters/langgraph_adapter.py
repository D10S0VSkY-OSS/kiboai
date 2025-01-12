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

        if not isinstance(inputs, dict):
            inputs = {"messages": [("user", str(inputs))]}

        result = self.graph.invoke(inputs)

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
        if not isinstance(inputs, dict):
            inputs = {"messages": [("user", str(inputs))]}

        result = await self.graph.ainvoke(inputs)

        output = "No output found"
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                last_msg = messages[-1]
                output = getattr(last_msg, "content", str(last_msg))
        else:
            output = str(result)

        return AgentResult(output_data=output, metadata={"adapter": "LangGraphAdapter"})
