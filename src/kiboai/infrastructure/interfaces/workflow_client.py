from kiboai.domain.blueprint import AgentConfig
from kiboai.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kiboai.application.workflow_factory import workflow_factory


def create_workflow(config: WorkflowConfig, api_key: str = None):
    """
    Creates an executable Adapter for the given workflow configuration.
    """
    return workflow_factory(config, api_key)
