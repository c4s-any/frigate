from pydantic import Field

from .base import FrigateBaseModel
from frigate.const import (
    MODEL_P_REID_PATH,
    MODEL_V_REID_PATH,
)

__all__ = ["ReidConfig"]

class ReidConfig(FrigateBaseModel):
    p_enabled: bool = Field(title="Enable Person REID.", default=False)
    v_enabled: bool = Field(title="Enable Vehicle REID.", default=False)
    shorter_size: int = Field(default=60, title="Snap Crop width")
    longer_size: int = Field(default=120, title="Snap Crop height")
    min_score_p: float = Field(default=0.8, title="Mini score for person reid")
    min_score_v: float = Field(default=0.8, title="Mini score for vehicle reid")
    p_model_path: str = Field(default=MODEL_P_REID_PATH, title="Person REID model path.")
    v_model_path: str = Field(default=MODEL_V_REID_PATH, title="Vehicle REID model path.")