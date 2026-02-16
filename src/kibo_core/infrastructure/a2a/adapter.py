import asyncio
from typing import Any, Optional, Tuple

from kibo_core.domain.entities import AgentRequest, AgentResult, AgentContext
from kibo_core.domain.ports import IAgentNode
from kibo_core.shared_kernel.logging import logger

import asyncio
from typing import Optional

from agno.client.a2a import A2AClient
from agno.os import AgentOS
from agno.os.interfaces.a2a import A2A
from kibo_core.domain.entities import AgentRequest, AgentResult
from kibo_core.domain.ports import IAgentNode
from kibo_core.shared_kernel.logging import logger


class AgnoA2AServerAdapter(IAgentNode):
    def __init__(
        self,
        agent,
        host: str,
        port: int,
        agent_id: str,
        access_log: bool,
    ):
        self.agent = agent
        self.host = host
        self.port = port
        self.agent_id = agent_id
        self.access_log = access_log

    def execute(self, request: AgentRequest) -> AgentResult:
        a2a = A2A(agents=[self.agent])
        agent_os = AgentOS(agents=[self.agent], interfaces=[a2a])
        app = agent_os.get_app()

        logger.info("Serving A2A on http://%s:%s", self.host, self.port)
        logger.info("Agent endpoint: /a2a/agents/%s/v1/message:send", self.agent_id)

        agent_os.serve(
            app=app, host=self.host, port=self.port, access_log=self.access_log
        )

        return AgentResult(
            output_data="Server stopped", metadata={"adapter": "agno-a2a"}
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        return self.execute(request)


class AgnoA2AClientAdapter(IAgentNode):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = A2AClient(base_url)

    def execute(self, request: AgentRequest) -> AgentResult:
        return asyncio.run(self.aexecute(request))

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        response = await self.client.send_message(message=str(request.input_data))
        return AgentResult(
            output_data=response,
            metadata={"source": "agno-a2a", "url": self.base_url},
        )
