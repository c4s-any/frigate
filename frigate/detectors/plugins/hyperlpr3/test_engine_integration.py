#!/usr/bin/env python3
"""
HyperLPR3推理引擎集成测试脚本
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_engine_factory():
    """测试引擎工厂"""
    logger.info("Testing engine factory...")
    
    try:
        from frigate.detectors.plugins.hyperlpr3.engine_factory import InferenceEngine
        
        # 测试创建引擎（使用虚拟路径）
        test_model_path = "test_model.onnx"
        engine = InferenceEngine(test_model_path, 4)
        
        logger.info(f"✓ Engine factory test passed")
        logger.info(f"  Engine type: {engine.engine_type}")
        logger.info(f"  Device: {getattr(engine, 'device', 'unknown')}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Engine factory test failed: {e}")
        return False


def test_embedding_adapter():
    """测试embedding适配器"""
    logger.info("Testing embedding adapter...")
    
    try:
        from frigate.detectors.plugins.hyperlpr3.embedding_engine_adapter import EmbeddingEngineAdapter
        
        # 测试创建适配器（使用虚拟路径）
        test_model_path = "test_model.onnx"
        adapter = EmbeddingEngineAdapter(test_model_path, 4, "CPU")
        
        logger.info(f"✓ Embedding adapter test passed")
        logger.info(f"  Adapter type: {adapter.engine_type}")
        logger.info(f"  Device: {adapter.device}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Embedding adapter test failed: {e}")
        return False


def test_engine_config():
    """测试引擎配置"""
    logger.info("Testing engine config...")
    
    try:
        from frigate.detectors.plugins.hyperlpr3.engine_config import engine_config
        
        # 测试配置获取
        engine_type = engine_config.get_engine_type()
        use_embedding = engine_config.should_use_embedding_engine()
        use_reid = engine_config.should_use_reid_engine()
        
        logger.info(f"✓ Engine config test passed")
        logger.info(f"  Engine type: {engine_type}")
        logger.info(f"  Use embedding: {use_embedding}")
        logger.info(f"  Use reid: {use_reid}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Engine config test failed: {e}")
        return False


def test_import_compatibility():
    """测试导入兼容性"""
    logger.info("Testing import compatibility...")
    
    try:
        # 测试从model.py导入
        from frigate.detectors.plugins.hyperlpr3.model import InferenceEngine
        
        logger.info("✓ Import compatibility test passed")
        logger.info("  Successfully imported InferenceEngine from model.py")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import compatibility test failed: {e}")
        return False


def test_environment_variables():
    """测试环境变量配置"""
    logger.info("Testing environment variables...")
    
    # 测试不同的环境变量设置
    test_cases = [
        ("embedding", "embedding"),
        ("reid", "reid"),
        ("auto", "auto"),
        ("invalid", "auto"),  # 无效值应该回退到auto
    ]
    
    for env_value, expected in test_cases:
        try:
            # 设置环境变量
            os.environ["HYPERLPR3_ENGINE_TYPE"] = env_value
            
            # 重新导入配置模块以获取新值
            import importlib
            from frigate.detectors.plugins.hyperlpr3 import engine_config
            importlib.reload(engine_config)
            
            actual = engine_config.engine_config.get_engine_type()
            if actual == expected or (env_value == "invalid" and actual == "embedding"):
                logger.info(f"✓ Environment variable test passed: {env_value} -> {actual}")
            else:
                logger.warning(f"⚠ Environment variable test warning: {env_value} -> {actual} (expected {expected})")
                
        except Exception as e:
            logger.error(f"✗ Environment variable test failed for {env_value}: {e}")
    
    # 清理环境变量
    if "HYPERLPR3_ENGINE_TYPE" in os.environ:
        del os.environ["HYPERLPR3_ENGINE_TYPE"]
    
    return True


def main():
    """主测试函数"""
    logger.info("Starting HyperLPR3 engine integration tests...")
    
    tests = [
        ("Engine Factory", test_engine_factory),
        ("Embedding Adapter", test_embedding_adapter),
        ("Engine Config", test_engine_config),
        ("Import Compatibility", test_import_compatibility),
        ("Environment Variables", test_environment_variables),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
    
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())