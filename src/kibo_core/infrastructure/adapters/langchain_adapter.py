from typing import Any, Dict
from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult
from langchain_core.runnables import Runnable

try:
    from langchain_community.callbacks import get_openai_callback
except ImportError:
    get_openai_callback = None


class LangChainAdapter(IAgentNode):
    """
    Adapter for LangChain Runnables (Chains, Graphs, Agents).
    """

    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Executes the LangChain runnable.
        Passes 'params' as config if needed, or just invokes with input data.
        """

        config = request.context.params.get("langchain_config", {})

        try:
            output_data = None
            metadata = {
                "adapter": "LangChainAdapter",
                "runnable_type": type(self.runnable).__name__,
            }

            if get_openai_callback:
                with get_openai_callback() as cb:
                    output_data = self.runnable.invoke(
                        request.input_data, config=config
                    )
                    metadata["cost"] = cb.total_cost
                    metadata["usage"] = {
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_tokens": cb.total_tokens,
                    }
            else:
                output_data = self.runnable.invoke(request.input_data, config=config)

            return AgentResult(output_data=output_data, metadata=metadata)
        except Exception as e:
            raise e

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        config = request.context.params.get("langchain_config", {})

        output_data = None
        metadata = {
            "adapter": "LangChainAdapter",
            "runnable_type": type(self.runnable).__name__,
        }

        if get_openai_callback:
            with get_openai_callback() as cb:
                output_data = await self.runnable.ainvoke(
                    request.input_data, config=config
                )
                metadata["cost"] = cb.total_cost
                metadata["usage"] = {
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_tokens": cb.total_tokens,
                }
        else:
            output_data = await self.runnable.ainvoke(request.input_data, config=config)

        return AgentResult(output_data=output_data, metadata=metadata)
