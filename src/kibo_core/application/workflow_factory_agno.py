import os
from typing import Any, Dict
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core.infrastructure.adapters.base import BaseAgentAdapter
from kibo_core.application.factory import agent_factory
from kibo_core.infrastructure.adapters.agno_adapter import AgnoAdapter


def _compile_workflow_to_agno(config: WorkflowConfig, api_key: str) -> BaseAgentAdapter:
    from agno.agent import Agent as AgnoAgent

    try:
        from agno.team import Team as AgnoTeam
    except ImportError:
        # Fallback if Team is not found, though usage of members implies Team class
        AgnoTeam = AgnoAgent

    from agno.models.openai import OpenAIChat

    sub_agents = []

    # 1. Create all sub-agents
    for step in config.steps:
        # Clone config to avoid mutation
        step_agent_config = step.agent.model_copy()
        step_agent_config.agent = "agno"  # Ensure we use Agno factory logic

        # We need the raw Agno Agent object, not the adapter
        adapter = agent_factory(step_agent_config, api_key)
        if hasattr(adapter, "agent"):
            agno_agent = adapter.agent
            # Ensure name is set for the team to reference it
            agno_agent.name = step_agent_config.name
            agno_agent.role = step_agent_config.description
            sub_agents.append(agno_agent)

    # 2. Create the Team/Manager Agent

    # Determine model for manager
    manager_model_id = config.config.get("manager_model", "gpt-4o")

    # Prepare native extensions but prioritize them over defaults if provided
    # Strategy: Merge native extensions with our defaults

    agent_kwargs = config.native_extensions.copy()

    # We set default instructions unless overridden in native extensions
    if "instructions" not in agent_kwargs:
        agent_kwargs["instructions"] = (
            f"You are the leader of the {config.name} team. Coordinate the team members to achieve the goal."
        )

    # We set other params but respect if user provided them in native_extensions
    if "name" not in agent_kwargs:
        agent_kwargs["name"] = config.name

    if "description" not in agent_kwargs:
        agent_kwargs["description"] = config.description

    # Model for Manager/Team Leader
    # If user provided a model in native_extensions, use it.
    # Checks if it is a string and needs wrapping (universal support)
    if "model" in agent_kwargs:
        model_val = agent_kwargs["model"]
        if isinstance(model_val, str):
            # Check if it's already in Agno format (provider:model) or LiteLLM format
            # If it has '/', it's likely LiteLLM format. Agno uses ':'
            # We wrap it in LiteLLM adapter to be safe and support universal providers
            from agno.models.litellm import LiteLLM

            # Pass api_key explicitly if available, otherwise LiteLLM might fallback to env
            # Note: api_key passed to factory might be OpenAI key or other.
            # If using native gemini string, we hope LiteLLM finds the key in env or we use the passed one.
            # But passed api_key might be inconsistent if manager uses differnt provider than agent.
            # However, for now, let's try to pass it if it seems relevant.
            agent_kwargs["model"] = LiteLLM(id=model_val, api_key=api_key)

    # Otherwise, resolve it using Kibo logic (String -> Proxy or LiteLLM Lib)
    elif "model" not in agent_kwargs:
        from agno.models.openai import OpenAIChat
        from agno.models.litellm import LiteLLM

        # Check for Kibo Proxy configuration (Environment)
        proxy_url = os.getenv("KIBO_PROXY_URL")
        final_api_key = api_key

        if proxy_url:
            base_url = proxy_url
            if not final_api_key:
                final_api_key = "sk-kibo-proxy"

            # Proxy Mode
            agent_kwargs["model"] = OpenAIChat(
                id=manager_model_id, api_key=final_api_key, base_url=base_url
            )
        else:
            # Universal Mode (LiteLLM Lib) or Native string resolution if supported
            # Here we wrap the string ID in a generic LiteLLM adapter which handles providers
            # e.g. "gemini/gemini-pro" -> LiteLLM(id="gemini/gemini-pro")
            agent_kwargs["model"] = LiteLLM(id=manager_model_id)

    if "markdown" not in agent_kwargs:
        agent_kwargs["markdown"] = True

    # Decide between Team and Agent
    team_leader = None

    if sub_agents:
        # It's a Team
        # Remove 'team' key if present in kwargs to avoid duplicate/error
        if "team" in agent_kwargs:
            del agent_kwargs["team"]

        # Add members
        agent_kwargs["members"] = sub_agents

        # Team might not support 'show_tool_calls', check if it's there
        if "show_tool_calls" in agent_kwargs:
            del agent_kwargs["show_tool_calls"]

        # Instantiate Team
        team_leader = AgnoTeam(**agent_kwargs)
    else:
        # Single Agent
        if "team" in agent_kwargs:
            del agent_kwargs["team"]

        if "show_tool_calls" not in agent_kwargs:
            agent_kwargs["show_tool_calls"] = True

        team_leader = AgnoAgent(**agent_kwargs)

    # Hook implementation (Strategy 2)
    if config.on_before_compile and callable(config.on_before_compile):
        config.on_before_compile(team_leader)

    return AgnoAdapter(team_leader)
