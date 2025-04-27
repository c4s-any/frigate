from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["hyperLpr3Config"]

class hyperLpr3Config(FrigateBaseModel):
    enabled: bool = Field(title="Enable hyperlpr3.", default=False)
    min_score: float = Field(default=0.6, title="Mini score for license plate identification")
    thread_num: int = Field(default=2, title="Thread num")