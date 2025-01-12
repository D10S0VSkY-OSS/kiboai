from typing import Any, Callable, Optional, Type
from pydantic import BaseModel, Field


class KiboTool(BaseModel):
    """
    Universal Tool definition for Kibo.
    Wraps a callable with metadata needed to register it across frameworks.
    """

    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    func: Callable[..., Any] = Field(..., description="The callable function")
    args_schema: Optional[Type[BaseModel]] = Field(
        None, description="Pydantic schema for arguments"
    )

    class Config:
        arbitrary_types_allowed = True

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)
