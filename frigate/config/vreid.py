from pydantic import Field

from .base import FrigateBaseModel
from frigate.const import (
    MODEL_V_REID_PATH,
)

__all__ = ["vReIDConfig"]

class vReIDConfig(FrigateBaseModel):
    enabled: bool = Field(title="Enable Vehicle ReID.", default=False)
    shorter_size: int = Field(default=60, title="Snap Crop width")
    longer_size: int = Field(default=120, title="Snap Crop height")
    min_score: float = Field(default=0.8, title="Mini score for vehicle ReID")
    model_path: str = Field(default=MODEL_V_REID_PATH, title="Vehicle ReID model path.")
    lang: str = Field(default="Simplified Chinese", title="Language used in character descriptions.")
    thread_num: int = Field(default=2, title="Number of threads")