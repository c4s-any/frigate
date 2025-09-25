"""
HyperLPR3推理引擎工厂类
根据配置自动选择合适的推理引擎
"""

import logging
from typing import Union

from .engine_config import engine_config

logger = logging.getLogger(__name__)


class HyperLPR3EngineFactory:
    """HyperLPR3推理引擎工厂"""
    
    @staticmethod
    def create_engine(onnx_path: str, thread_num: int):
        """
        创建推理引擎实例
        
        Args:
            onnx_path: ONNX模型路径
            thread_num: 线程数
            
        Returns:
            推理引擎实例
        """
        # 只支持embedding引擎
        return HyperLPR3EngineFactory._create_embedding_engine(onnx_path, thread_num)
    
    @staticmethod
    def _create_embedding_engine(onnx_path: str, thread_num: int):
        """创建embedding推理引擎"""
        try:
            from .embedding_engine_adapter import InferenceEngine
            logger.info("Creating embedding-based inference engine")
            return InferenceEngine(onnx_path, thread_num)
        except ImportError as e:
            logger.error(f"Failed to create embedding engine: {e}")
            logger.error("Please ensure embedding modules are available. Install required dependencies:")
            logger.error("  - frigate embedding dependencies")
            logger.error("  - ONNX Runtime or OpenVINO")
            raise
    
    @staticmethod
    def _create_reid_engine(onnx_path: str, thread_num: int):
        """创建reid推理引擎（已弃用，建议使用embedding引擎）"""
        logger.error("Reid engine is deprecated. Please use embedding engine instead.")
        logger.error("Set HYPERLPR3_ENGINE_TYPE=embedding to use the recommended engine.")
        raise ImportError("Reid engine is no longer supported. Please use embedding engine.")


# 为了向后兼容，提供InferenceEngine的别名
def InferenceEngine(onnx_path: str, thread_num: int):
    """向后兼容的InferenceEngine函数"""
    return HyperLPR3EngineFactory.create_engine(onnx_path, thread_num)