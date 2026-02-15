from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core.application.workflow_factory import workflow_factory


def create_workflow(config: WorkflowConfig, api_key: str = None):
    """
    Creates an executable Adapter for the given workflow configuration.
    """
    return workflow_factory(config, api_key)
