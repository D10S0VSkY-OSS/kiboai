from dataclasses import dataclass
from typing import Any, Dict, Optional
import os

from kibo_core.domain.entities import AgentRequest, AgentResult
from kibo_core.domain.ports import IAgentNode
from kibo_core.shared_kernel.logging import logger


@dataclass(frozen=True)
class LangfuseConfig:
    enabled: bool = True
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    host: Optional[str] = None
    trace_name: Optional[str] = None
    tags: Optional[list[str]] = None

    def resolved_public_key(self) -> Optional[str]:
        return self.public_key or os.getenv("LANGFUSE_PUBLIC_KEY")

    def resolved_secret_key(self) -> Optional[str]:
        return self.secret_key or os.getenv("LANGFUSE_SECRET_KEY")

    def resolved_host(self) -> Optional[str]:
        return self.host or os.getenv("LANGFUSE_HOST")


def normalize_langfuse_config(value: Any) -> Optional[LangfuseConfig]:
    if isinstance(value, LangfuseConfig):
        return value
    if isinstance(value, dict):
        return LangfuseConfig(**value)
    return None


class LangfuseTracingAdapter(IAgentNode):
    def __init__(self, adapter: IAgentNode, config: LangfuseConfig, agent_name: str):
        self.adapter = adapter
        self.config = config
        self.agent_name = agent_name
        self._client = None

    def _get_client(self):
        if not self.config.enabled:
            return None
        if self._client is not None:
            return self._client

        public_key = self.config.resolved_public_key()
        secret_key = self.config.resolved_secret_key()
        host = self.config.resolved_host()

        if not public_key or not secret_key or not host:
            logger.warning("Langfuse config is incomplete. Skipping tracing.")
            return None

        try:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
            )
        except Exception as exc:
            logger.warning("Failed to initialize Langfuse client: %s", exc)
            self._client = None

        return self._client

    def execute(self, request: AgentRequest) -> AgentResult:
        client = self._get_client()
        if client is None:
            return self.adapter.execute(request)

        trace_name = self.config.trace_name or f"kibo.{self.agent_name}"
        span = client.start_span(
            name=trace_name,
            input=request.input_data,
            metadata={"agent": self.agent_name, "tags": self.config.tags or []},
        )

        try:
            result = self.adapter.execute(request)
            span.update(output=result.output_data)
            trace_id = getattr(span, "trace_id", None)
            if trace_id:
                result.metadata = result.metadata or {}
                result.metadata["langfuse_trace_id"] = trace_id
            return result
        except Exception as exc:
            span.update(metadata={"error": str(exc)})
            raise
        finally:
            try:
                span.end()
                client.flush()
            except Exception:
                pass

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        client = self._get_client()
        if client is None:
            return await self.adapter.aexecute(request)

        trace_name = self.config.trace_name or f"kibo.{self.agent_name}"
        span = client.start_span(
            name=trace_name,
            input=request.input_data,
            metadata={"agent": self.agent_name, "tags": self.config.tags or []},
        )

        try:
            result = await self.adapter.aexecute(request)
            span.update(output=result.output_data)
            trace_id = getattr(span, "trace_id", None)
            if trace_id:
                result.metadata = result.metadata or {}
                result.metadata["langfuse_trace_id"] = trace_id
            return result
        except Exception as exc:
            span.update(metadata={"error": str(exc)})
            raise
        finally:
            try:
                span.end()
                client.flush()
            except Exception:
                pass
