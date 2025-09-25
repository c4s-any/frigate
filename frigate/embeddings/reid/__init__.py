"""
ReID Embedding Module

将ReID功能集成到embedding模块中，使用统一的推理引擎
"""

from .reid_embedding_engine import ReIDEmbeddingEngine
from .reid_processor import ReIDProcessor
from .reid_inference_engine import InferenceEngine, create_inference_engine
from frigate.tools.encryption.model_decryptor_advanced import ModelDecryptor

__all__ = ['ReIDEmbeddingEngine', 'ReIDProcessor', 'InferenceEngine', 'create_inference_engine', 'ModelDecryptor']
