# cython:language_level=3
import os

import onnxruntime as ort
try:
    import tensorrt as trt
except ModuleNotFoundError:
    print("No cuda devices.")
try:
    from tflite_runtime.interpreter import Interpreter
except ModuleNotFoundError:
    from tensorflow.lite.python.interpreter import Interpreter

# 注意：解密功能已迁移到 model_decryptor_advanced.py
# 此文件现在只提供基本的会话初始化功能

def init_onnx_session(path, providers, options):
    """
    初始化ONNX Runtime会话
    
    注意：此函数现在只处理普通模型文件
    加密模型请使用 model_decryptor_advanced.py 中的高级解密功能
    """
    session = ort.InferenceSession(path, providers=providers, provider_options=options)
    return session

def init_trt_session(path, logger):
    """
    初始化TensorRT会话
    
    注意：此函数现在只处理普通模型文件
    加密模型请使用 model_decryptor_advanced.py 中的高级解密功能
    """
    with trt.Runtime(logger) as runtime:
        return runtime.deserialize_cuda_engine(path)

def init_tflite_session(path, delegates):
    """
    初始化TFLite会话
    
    注意：此函数现在只处理普通模型文件
    加密模型请使用 model_decryptor_advanced.py 中的高级解密功能
    """
    session = Interpreter(
        model_path=path,
        experimental_delegates=delegates,
    )
    return session
