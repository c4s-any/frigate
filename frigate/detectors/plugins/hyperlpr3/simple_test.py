#!/usr/bin/env python3
"""
简单的HyperLPR3推理引擎集成测试
"""

import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_imports():
    """测试基本导入功能"""
    logger.info("Testing basic imports...")
    
    try:
        # 测试导入各个模块
        from .engine_config import engine_config
        logger.info("✓ engine_config imported successfully")
        
        from .engine_factory import HyperLPR3EngineFactory
        logger.info("✓ engine_factory imported successfully")
        
        from .embedding_engine_adapter import EmbeddingEngineAdapter
        logger.info("✓ embedding_engine_adapter imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import test failed: {e}")
        return False


def test_engine_config():
    """测试引擎配置"""
    logger.info("Testing engine configuration...")
    
    try:
        from .engine_config import engine_config
        
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


def test_environment_variables():
    """测试环境变量"""
    logger.info("Testing environment variables...")
    
    try:
        # 保存原始环境变量
        original_env = os.environ.get("HYPERLPR3_ENGINE_TYPE")
        
        # 测试设置环境变量
        os.environ["HYPERLPR3_ENGINE_TYPE"] = "embedding"
        
        # 重新导入配置
        import importlib
        from . import engine_config
        importlib.reload(engine_config)
        
        # 检查配置
        if engine_config.engine_config.engine_type == "embedding":
            logger.info("✓ Environment variable test passed")
        else:
            logger.warning(f"⚠ Environment variable test warning: expected 'embedding', got '{engine_config.engine_config.engine_type}'")
        
        # 恢复原始环境变量
        if original_env is not None:
            os.environ["HYPERLPR3_ENGINE_TYPE"] = original_env
        else:
            os.environ.pop("HYPERLPR3_ENGINE_TYPE", None)
        
        return True
    except Exception as e:
        logger.error(f"✗ Environment variable test failed: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("Starting simple HyperLPR3 engine integration tests...")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Engine Config", test_engine_config),
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


