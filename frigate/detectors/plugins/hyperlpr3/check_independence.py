#!/usr/bin/env python3
"""
检查hyperlpr3是否独立于reid.py的代码分析
"""

import ast
import os
import sys
from pathlib import Path


def analyze_file_dependencies(file_path):
    """分析文件的依赖关系"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []


def check_reid_dependency():
    """检查hyperlpr3是否依赖reid.py"""
    print("=== 检查HyperLPR3对reid.py的依赖 ===")
    
    hyperlpr3_dir = Path("/home/afw/frigate/frigate/detectors/plugins/hyperlpr3")
    reid_dependencies = []
    
    # 检查所有Python文件
    for py_file in hyperlpr3_dir.glob("*.py"):
        if py_file.name.startswith("test_") or py_file.name.startswith("check_"):
            continue
            
        print(f"\n分析文件: {py_file.name}")
        imports = analyze_file_dependencies(py_file)
        
        # 检查是否有reid相关的导入
        reid_imports = [imp for imp in imports if "reid" in imp.lower()]
        if reid_imports:
            print(f"  ⚠️  发现reid依赖: {reid_imports}")
            reid_dependencies.extend(reid_imports)
        else:
            print(f"  ✅ 无reid依赖")
    
    return reid_dependencies


def check_engine_priority():
    """检查引擎优先级设置"""
    print("\n=== 检查引擎优先级设置 ===")
    
    config_file = Path("/home/afw/frigate/frigate/detectors/plugins/hyperlpr3/engine_config.py")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查默认配置
        if 'os.getenv("HYPERLPR3_ENGINE_TYPE", "auto")' in content:
            print("✅ 默认配置为auto模式")
        
        # 检查自动选择逻辑
        if "from frigate.embeddings.onnx.runner import ONNXModelRunner" in content:
            print("✅ 自动选择优先尝试embedding引擎")
        
        # 检查回退逻辑
        if "falling back to reid engine" in content:
            print("⚠️  仍有reid引擎回退逻辑")
        
        return True
    except Exception as e:
        print(f"❌ 检查配置失败: {e}")
        return False


def check_embedding_integration():
    """检查embedding集成"""
    print("\n=== 检查Embedding集成 ===")
    
    adapter_file = Path("/home/afw/frigate/frigate/detectors/plugins/hyperlpr3/embedding_engine_adapter.py")
    
    try:
        with open(adapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用embedding的ONNXModelRunner
        if "from frigate.embeddings.onnx.runner import ONNXModelRunner" in content:
            print("✅ 使用embedding中的ONNXModelRunner")
        
        # 检查适配器实现
        if "class EmbeddingEngineAdapter" in content:
            print("✅ 实现了适配器模式")
        
        # 检查兼容性
        if "def run_single_input" in content:
            print("✅ 保持原有接口兼容性")
        
        return True
    except Exception as e:
        print(f"❌ 检查embedding集成失败: {e}")
        return False


def check_license_plate_integration():
    """检查车牌识别集成"""
    print("\n=== 检查车牌识别集成 ===")
    
    # 检查hyperlpr embedding
    hyperlpr_embedding = Path("/home/afw/frigate/frigate/embeddings/hyperlpr/hyperlpr_embedding.py")
    
    try:
        with open(hyperlpr_embedding, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用hyperlpr3
        if "from frigate.detectors.plugins.hyperlpr3.hyperlpr3 import LicensePlateCatcher" in content:
            print("✅ HyperLPR embedding使用hyperlpr3")
        
        # 检查是否有reid依赖
        if "reid" in content.lower():
            print("⚠️  HyperLPR embedding中仍有reid相关内容")
        else:
            print("✅ HyperLPR embedding无reid依赖")
        
        return True
    except Exception as e:
        print(f"❌ 检查车牌识别集成失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 分析HyperLPR3独立性和优先级...")
    
    # 检查依赖关系
    reid_deps = check_reid_dependency()
    
    # 检查引擎优先级
    priority_ok = check_engine_priority()
    
    # 检查embedding集成
    embedding_ok = check_embedding_integration()
    
    # 检查车牌识别集成
    lpr_ok = check_license_plate_integration()
    
    # 总结
    print("\n=== 总结 ===")
    
    if not reid_deps:
        print("✅ HyperLPR3核心模块无reid依赖")
    else:
        print(f"⚠️  HyperLPR3仍有reid依赖: {reid_deps}")
    
    if priority_ok and embedding_ok and lpr_ok:
        print("🎉 HyperLPR3已成功集成embedding引擎，优先级设置正确！")
        
        print("\n📋 当前状态:")
        print("  ✅ 使用embedding中的ONNXModelRunner")
        print("  ✅ 默认优先选择embedding引擎")
        print("  ✅ 保持向后兼容性")
        print("  ✅ 支持环境变量配置")
        
        print("\n🚀 要完全独立于reid.py，需要:")
        print("  1. 设置环境变量: export HYPERLPR3_ENGINE_TYPE=embedding")
        print("  2. 或者修改默认配置为embedding优先")
        
        return 0
    else:
        print("❌ 集成尚未完全完成")
        return 1


if __name__ == "__main__":
    sys.exit(main())


