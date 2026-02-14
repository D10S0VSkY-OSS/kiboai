# Monkeypatch for LiteLLM bug on Python 3.13 (AttributeError: __annotations__)
try:
    import litellm.litellm_core_utils.model_param_helper

    def _patched_get_transcription_kwargs():
        return set()

    litellm.litellm_core_utils.model_param_helper.ModelParamHelper._get_litellm_supported_transcription_kwargs = staticmethod(
        _patched_get_transcription_kwargs
    )
except (ImportError, AttributeError):
    pass

from .infrastructure.runtime import kibo_init as init
from .infrastructure.runtime import get

from .application.workflow import DistributedWorkflowService
from .application.factory import create_distributed_agent
from .domain.entities import AgentRequest, AgentResult, AgentContext
from .domain.ports import IAgentNode
from .domain.blueprint import AgentConfig
from .infrastructure.interfaces.client import KiboAgent, create_agent
from .infrastructure.interfaces.workflow_client import create_workflow

from .infrastructure.adapters.base import LazyAgentAdapter
from .infrastructure.adapters.agno_adapter import AgnoAdapter
from .infrastructure.adapters.pydantic_ai_adapter import PydanticAIAdapter
from .infrastructure.adapters.langgraph_adapter import LangGraphAdapter

__all__ = [
    "init",
    "get",
    "DistributedWorkflowService",
    "create_distributed_agent",
    "AgentConfig",
    "KiboAgent",
    "create_agent",
    "create_workflow",
    "AgentRequest",
    "AgentResult",
    "AgentContext",
    "IAgentNode",
    "LazyAgentAdapter",
    "AgnoAdapter",
    "PydanticAIAdapter",
    "LangGraphAdapter",
]
