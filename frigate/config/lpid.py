from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["LpidConfig"]

class LpidConfig(FrigateBaseModel):
    enabled: bool = Field(title="Enable LPID.", default=False)
    min_score: float = Field(default=0.6, title="Mini score for license plate identification")