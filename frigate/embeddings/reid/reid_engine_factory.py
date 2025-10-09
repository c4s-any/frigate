"""
ReID引擎工厂

根据配置创建相应的推理引擎实例
支持embedding引擎和传统reid引擎
"""

import logging
from typing import Union

from .reid_engine_config import engine_config

logger = logging.getLogger(__name__)


class ReIDEngineFactory:
    """ReID推理引擎工厂"""
    
    @staticmethod
    def create_engine(onnx_path: str, thread_num: int, metrics=None):
        """
        创建推理引擎实例
        
        Args:
            onnx_path: ONNX模型路径
            thread_num: 线程数
            metrics: 性能指标对象（可选）
            
        Returns:
            推理引擎实例
        """
        if engine_config.should_use_embedding_engine():
            return ReIDEngineFactory._create_embedding_engine(onnx_path, thread_num, metrics)
        elif engine_config.should_use_reid_engine():
            return ReIDEngineFactory._create_reid_engine(onnx_path, thread_num, metrics)
        else:
            # 默认使用embedding引擎
            return ReIDEngineFactory._create_embedding_engine(onnx_path, thread_num, metrics)
    
    @staticmethod
    def _create_embedding_engine(onnx_path: str, thread_num: int, metrics=None):
        """创建embedding推理引擎"""
        try:
            from .reid_embedding_adapter import ReIDEmbeddingAdapter
            logger.info("Creating embedding-based inference engine")
            return ReIDEmbeddingAdapter(onnx_path, thread_num, metrics)
        except ImportError as e:
            logger.error(f"Failed to create embedding engine: {e}")
            logger.error("Please ensure embedding modules are available. Install required dependencies:")
            logger.error("  - frigate embedding dependencies")
            logger.error("  - ONNX Runtime or OpenVINO")
            raise
    
    @staticmethod
    def _create_reid_engine(onnx_path: str, thread_num: int, metrics=None):
        """创建reid推理引擎"""
        try:
            from .reid import InferenceEngine
            logger.info("Creating reid-based inference engine")
            return InferenceEngine(onnx_path, thread_num, metrics)
        except ImportError as e:
            logger.error(f"Failed to create reid engine: {e}")
            raise


def InferenceEngine(onnx_path: str, thread_num: int, metrics=None):
    """
    创建推理引擎的便捷函数
    
    Args:
        onnx_path: ONNX模型路径
        thread_num: 线程数
        metrics: 性能指标对象（可选）
        
    Returns:
        推理引擎实例
    """
    return ReIDEngineFactory.create_engine(onnx_path, thread_num, metrics)
