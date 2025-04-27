from pydantic import Field

from .base import FrigateBaseModel
from frigate.const import (
    MODEL_P_REID_PATH,
)

__all__ = ["pReIDConfig"]

class pReIDConfig(FrigateBaseModel):
    enabled: bool = Field(title="Enable pedestrian ReID.", default=False)
    square_snap_enabled: bool = Field(title="Enable/Disable person square snap frame.", default=False)
    shorter_size: int = Field(default=60, title="Snap crop width")
    longer_size: int = Field(default=120, title="Snap crop height")
    min_score: float = Field(default=0.8, title="Mini score for pedestrian ReID")
    model_path: str = Field(default=MODEL_P_REID_PATH, title="Pedestrian ReID model path.")
    lang: str = Field(default="Simplified Chinese", title="Language used in character descriptions.")
    thread_num: int = Field(default=2, title="Number of threads")