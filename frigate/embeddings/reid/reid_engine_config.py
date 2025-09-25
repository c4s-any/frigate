"""
ReID引擎配置管理

管理ReID推理引擎的选择和配置
支持在传统引擎和embedding引擎之间切换
"""

import os
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# 推理引擎类型
EngineType = Literal["embedding", "reid", "auto"]

class ReIDEngineConfig:
    """ReID推理引擎配置"""
    
    def __init__(self):
        # 从环境变量读取配置，默认为embedding（优先使用embedding引擎）
        self.engine_type = os.getenv("REID_ENGINE_TYPE", "embedding").lower()
        
        # 验证配置
        if self.engine_type not in ["embedding", "reid", "auto"]:
            logger.warning(f"Invalid engine type: {self.engine_type}, falling back to embedding")
            self.engine_type = "embedding"
        
        logger.info(f"ReID engine type: {self.engine_type}")
    
    def get_engine_type(self) -> EngineType:
        """获取推理引擎类型"""
        if self.engine_type == "auto":
            return self._auto_select_engine()
        return self.engine_type
    
    def _auto_select_engine(self) -> EngineType:
        """自动选择推理引擎"""
        try:
            # 尝试导入embedding引擎
            from frigate.embeddings.onnx.runner import ONNXModelRunner
            logger.info("Auto-selected embedding engine")
            return "embedding"
        except ImportError:
            logger.warning("Embedding engine not available, falling back to reid engine")
            return "reid"
    
    def should_use_embedding_engine(self) -> bool:
        """是否应该使用embedding引擎"""
        return self.get_engine_type() == "embedding"
    
    def should_use_reid_engine(self) -> bool:
        """是否应该使用reid引擎"""
        return self.get_engine_type() == "reid"


# 全局配置实例
engine_config = ReIDEngineConfig()
