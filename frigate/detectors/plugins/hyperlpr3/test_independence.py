#!/usr/bin/env python3
"""
测试hyperlpr3是否独立于reid.py运行
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_hyperlpr3_independence():
    """测试hyperlpr3是否独立于reid.py"""
    logger.info("Testing HyperLPR3 independence from reid.py...")
    
    # 保存原始reid.py路径
    reid_path = Path("/home/afw/frigate/frigate/detectors/plugins/reid.py")
    backup_path = Path("/home/afw/frigate/frigate/detectors/plugins/reid.py.backup")
    
    try:
        # 1. 备份reid.py
        if reid_path.exists():
            shutil.copy2(reid_path, backup_path)
            logger.info("✓ Backed up reid.py")
        
        # 2. 临时删除reid.py
        if reid_path.exists():
            reid_path.unlink()
            logger.info("✓ Temporarily removed reid.py")
        
        # 3. 测试hyperlpr3是否能正常工作
        try:
            # 设置环境变量强制使用embedding引擎
            os.environ["HYPERLPR3_ENGINE_TYPE"] = "embedding"
            
            # 测试导入
            sys.path.insert(0, "/home/afw/frigate")
            
            # 测试引擎配置
            from frigate.detectors.plugins.hyperlpr3.engine_config import engine_config
            engine_type = engine_config.get_engine_type()
            logger.info(f"✓ Engine config works: {engine_type}")
            
            # 测试引擎工厂
            from frigate.detectors.plugins.hyperlpr3.engine_factory import HyperLPR3EngineFactory
            logger.info("✓ Engine factory imported successfully")
            
            # 测试embedding适配器
            from frigate.detectors.plugins.hyperlpr3.embedding_engine_adapter import EmbeddingEngineAdapter
            logger.info("✓ Embedding adapter imported successfully")
            
            # 测试hyperlpr3主模块
            from frigate.detectors.plugins.hyperlpr3.hyperlpr3 import LicensePlateCatcher
            logger.info("✓ HyperLPR3 main module imported successfully")
            
            # 测试hyperlpr embedding
            from frigate.embeddings.hyperlpr.hyperlpr_embedding import HyperLPRModelRunner
            logger.info("✓ HyperLPR embedding imported successfully")
            
            logger.info("🎉 HyperLPR3 works independently without reid.py!")
            return True
            
        except Exception as e:
            logger.error(f"✗ HyperLPR3 failed without reid.py: {e}")
            return False
            
    finally:
        # 4. 恢复reid.py
        if backup_path.exists():
            shutil.copy2(backup_path, reid_path)
            backup_path.unlink()
            logger.info("✓ Restored reid.py")
        
        # 清理环境变量
        if "HYPERLPR3_ENGINE_TYPE" in os.environ:
            del os.environ["HYPERLPR3_ENGINE_TYPE"]


def test_engine_priority():
    """测试引擎优先级"""
    logger.info("Testing engine priority...")
    
    try:
        # 测试默认配置（auto模式）
        os.environ.pop("HYPERLPR3_ENGINE_TYPE", None)
        
        sys.path.insert(0, "/home/afw/frigate")
        
        # 重新导入配置以获取默认值
        import importlib
        from frigate.detectors.plugins.hyperlpr3 import engine_config
        importlib.reload(engine_config)
        
        engine_type = engine_config.engine_config.get_engine_type()
        logger.info(f"✓ Default engine type: {engine_type}")
        
        # 测试embedding引擎优先级
        if engine_type == "embedding":
            logger.info("🎉 Embedding engine is prioritized by default!")
            return True
        else:
            logger.warning(f"⚠ Default engine is {engine_type}, not embedding")
            return False
            
    except Exception as e:
        logger.error(f"✗ Engine priority test failed: {e}")
        return False


def test_license_plate_integration():
    """测试车牌识别集成"""
    logger.info("Testing license plate recognition integration...")
    
    try:
        sys.path.insert(0, "/home/afw/frigate")
        
        # 测试车牌识别模型运行器
        from frigate.data_processing.common.license_plate.model import LicensePlateModelRunner
        logger.info("✓ License plate model runner imported successfully")
        
        # 测试hyperlpr embedding
        from frigate.embeddings.hyperlpr.hyperlpr_embedding import HyperLPRModelRunner
        logger.info("✓ HyperLPR model runner imported successfully")
        
        logger.info("🎉 License plate recognition integration works!")
        return True
        
    except Exception as e:
        logger.error(f"✗ License plate integration test failed: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("Starting HyperLPR3 independence tests...")
    
    tests = [
        ("HyperLPR3 Independence", test_hyperlpr3_independence),
        ("Engine Priority", test_engine_priority),
        ("License Plate Integration", test_license_plate_integration),
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
        logger.info("🎉 All tests passed! HyperLPR3 is independent and prioritized!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())


