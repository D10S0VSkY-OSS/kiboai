from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class A2AConfig:
    enabled: bool = True
    mode: str = "server"  # "server" or "client"
    host: str = "localhost"
    port: int = 7777
    agent_id: str = "server-bot"
    base_url: Optional[str] = None
    access_log: bool = True

    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url
        return f"http://{self.host}:{self.port}/a2a/agents/{self.agent_id}"
