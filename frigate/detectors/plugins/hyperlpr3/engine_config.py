"""
HyperLPR3推理引擎配置模块
"""

import os
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# 推理引擎类型
EngineType = Literal["embedding", "auto"]

class HyperLPR3EngineConfig:
    """HyperLPR3推理引擎配置"""
    
    def __init__(self):
        # 从环境变量读取配置，默认为embedding（优先使用embedding引擎）
        self.engine_type = os.getenv("HYPERLPR3_ENGINE_TYPE", "embedding").lower()
        
        # 验证配置
        if self.engine_type not in ["embedding", "auto"]:
            logger.warning(f"Invalid engine type: {self.engine_type}, falling back to embedding")
            self.engine_type = "embedding"
        
        logger.info(f"HyperLPR3 engine type: {self.engine_type}")
    
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
            logger.error("Embedding engine not available. Please install required dependencies.")
            raise ImportError("Embedding engine is required but not available. Please install frigate embedding dependencies.")
    
    def should_use_embedding_engine(self) -> bool:
        """是否应该使用embedding引擎"""
        return self.get_engine_type() == "embedding"
    
    def should_use_reid_engine(self) -> bool:
        """是否应该使用reid引擎（已弃用）"""
        logger.warning("Reid engine is deprecated. Please use embedding engine instead.")
        return False


# 全局配置实例
engine_config = HyperLPR3EngineConfig()