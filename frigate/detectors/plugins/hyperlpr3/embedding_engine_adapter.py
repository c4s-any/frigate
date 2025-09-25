"""
适配器模块：让hyperlpr3使用embedding中的ONNXModelRunner
"""

import logging
import os
from typing import Any, Dict, Optional

import numpy as np
import onnxruntime as ort
from openvino.runtime import Core, Tensor

from frigate.embeddings.onnx.runner import ONNXModelRunner
from frigate.util.model import get_ort_providers

logger = logging.getLogger(__name__)


class EmbeddingEngineAdapter:
    """
    适配器类：将embedding中的ONNXModelRunner适配为hyperlpr3可用的推理引擎
    保持与原有InferenceEngine相同的接口
    """
    
    def __init__(self, onnx_path: str, thread_num: int, device: str = "AUTO"):
        """
        初始化适配器
        
        Args:
            onnx_path: ONNX模型路径
            thread_num: 线程数
            device: 设备类型 (AUTO, CPU, GPU, etc.)
        """
        self.onnx_path = onnx_path
        self.threads = thread_num
        self.device = self._normalize_device(device)
        
        # 使用embedding中的ONNXModelRunner
        self.runner = ONNXModelRunner(
            model_path=onnx_path,
            device=self.device,
            requires_fp16=False  # 根据模型需要调整
        )
        
        # 为了兼容性，设置session属性
        self.session = self.runner
        self.engine_type = self.runner.type
        
        # 添加inputs和outputs属性（兼容OpenVINO接口）
        if self.runner.type == "ov":
            self.inputs = self.runner.interpreter.inputs
            self.outputs = self.runner.interpreter.outputs
        else:
            # ONNX Runtime格式，创建兼容的属性
            self.inputs = self.runner.ort.get_inputs()
            self.outputs = self.runner.ort.get_outputs()
        
        logger.info(f"EmbeddingEngineAdapter initialized with {self.engine_type} backend")
    
    def _normalize_device(self, device: str) -> str:
        """标准化设备名称"""
        device_mapping = {
            "cuda": "GPU",
            "openvino": "GPU",  # OpenVINO GPU
            "cpu": "CPU",
            "auto": "AUTO"
        }
        return device_mapping.get(device.lower(), device.upper())
    
    def get_input_names(self) -> list[str]:
        """获取输入名称"""
        return self.runner.get_input_names()
    
    def get_inputs(self):
        """获取输入信息（兼容ONNX Runtime接口）"""
        if self.runner.type == "ov":
            # OpenVINO格式
            return self.runner.interpreter.inputs
        else:
            # ONNX Runtime格式
            return self.runner.ort.get_inputs()
    
    def get_outputs(self):
        """获取输出信息（兼容ONNX Runtime接口）"""
        if self.runner.type == "ov":
            # OpenVINO格式
            return self.runner.interpreter.outputs
        else:
            # ONNX Runtime格式
            return self.runner.ort.get_outputs()
    
    def get_input_width(self) -> int:
        """获取输入宽度"""
        return self.runner.get_input_width()
    
    def create_infer_request(self):
        """创建推理请求（兼容OpenVINO接口）"""
        if self.runner.type == "ov":
            return self.runner.interpreter.create_infer_request()
        else:
            # ONNX Runtime不需要create_infer_request，返回self
            return self
    
    def run(self, output_names=None, inputs: Dict[str, Any] = None) -> Any:
        """
        运行推理（兼容ONNX Runtime接口）
        
        Args:
            output_names: 输出名称列表（可选，用于ONNX Runtime兼容性）
            inputs: 输入数据字典
            
        Returns:
            推理结果
        """
        # 处理不同的调用方式
        if output_names is not None and inputs is not None:
            # ONNX Runtime格式：run(output_names, inputs)
            if self.runner.type == "ort":
                return self.runner.ort.run(output_names, inputs)
            else:
                # OpenVINO格式，忽略output_names
                return self.runner.run(inputs)
        elif inputs is not None:
            # 直接传入inputs字典
            return self.runner.run(inputs)
        else:
            raise ValueError("Invalid arguments for run method")
    
    def run_single_input(self, input_data: np.ndarray, input_name: str = None) -> Any:
        """
        运行单输入推理（兼容原有接口）
        
        Args:
            input_data: 输入数据
            input_name: 输入名称，如果为None则使用第一个输入
            
        Returns:
            推理结果
        """
        if input_name is None:
            input_names = self.get_input_names()
            if not input_names:
                raise ValueError("No input names found")
            input_name = input_names[0]
        
        inputs = {input_name: input_data}
        return self.run(inputs)
    
    def load_model_content_or_model_path(self):
        """兼容原有接口，返回模型路径"""
        return self.onnx_path


class HyperLPR3EmbeddingEngine:
    """
    HyperLPR3专用的embedding推理引擎
    提供与原有InferenceEngine相同的接口
    """
    
    def __init__(self, onnx_path: str, thread_num: int):
        """
        初始化推理引擎
        
        Args:
            onnx_path: ONNX模型路径
            thread_num: 线程数
        """
        self.onnx_path = onnx_path
        self.threads = thread_num
        
        # 自动选择设备
        self.device = self._select_device()
        
        # 创建适配器
        self.adapter = EmbeddingEngineAdapter(
            onnx_path=onnx_path,
            thread_num=thread_num,
            device=self.device
        )
        
        # 为了兼容性，设置session属性
        self.session = self.adapter
        self.engine_type = self.adapter.engine_type
        
        logger.info(f"HyperLPR3EmbeddingEngine initialized with {self.engine_type} backend")
    
    def _select_device(self) -> str:
        """自动选择最优设备"""
        # 获取可用的providers
        providers = ort.get_available_providers()
        
        # 优先级策略
        if 'CUDAExecutionProvider' in providers:
            return "GPU"
        
        # 检查OpenVINO GPU
        try:
            core = Core()
            gpu_devices = [d for d in core.available_devices if d.startswith("GPU")]
            if gpu_devices:
                return "GPU"
        except Exception:
            pass
        
        # 回退到CPU
        return "CPU"
    
    def get_input_names(self) -> list[str]:
        """获取输入名称"""
        return self.adapter.get_input_names()
    
    def get_input_width(self) -> int:
        """获取输入宽度"""
        return self.adapter.get_input_width()
    
    def run(self, inputs: Dict[str, Any]) -> Any:
        """运行推理"""
        return self.adapter.run(inputs)
    
    def run_single_input(self, input_data: np.ndarray, input_name: str = None) -> Any:
        """运行单输入推理"""
        return self.adapter.run_single_input(input_data, input_name)
    
    def load_model_content_or_model_path(self):
        """返回模型路径"""
        return self.onnx_path


# 为了向后兼容，提供InferenceEngine的别名
InferenceEngine = HyperLPR3EmbeddingEngine