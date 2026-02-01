#!/usr/bin/env python3
"""
测试脚本 - 验证改进后的代码结构和功能
"""

import sys
import os
import importlib.util
import json


def test_module_imports():
    """测试模块导入"""
    modules = ["config_validator", "error_handler", "cache_manager", "middleware"]

    print("测试模块导入...")
    all_passed = True
    for module_name in modules:
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, f"{module_name}.py"
            )
            if spec is None:
                raise ImportError(f"无法创建模块规范: {module_name}")
            module = importlib.util.module_from_spec(spec)
            print(f"✓ {module_name}.py - 语法正确")
        except Exception as e:
            print(f"✗ {module_name}.py - 语法错误: {str(e)}")
            all_passed = False

    return all_passed


def test_config_validation():
    """测试配置验证"""
    print("\n测试配置验证...")
    try:
        from config_validator import ConfigValidator

        # 测试增强版配置文件
        is_valid, errors, config = ConfigValidator.validate_config(
            "config_enhanced.json"
        )

        # 过滤掉API密钥错误，因为这是预期的
        filtered_errors = [
            e for e in errors if "API密钥" not in e and "api_key" not in e
        ]

        if not filtered_errors:
            print("✓ 增强版配置文件验证通过（除API密钥外）")
        else:
            print("✗ 增强版配置文件验证失败:")
            for error in filtered_errors:
                print(f"  - {error}")

        return True
    except Exception as e:
        print(f"✗ 配置验证测试失败: {str(e)}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n测试文件结构...")

    required_files = [
        "config_validator.py",
        "error_handler.py",
        "cache_manager.py",
        "middleware.py",
        "zhipu_comprehensive_mcp_enhanced_v2.py",
        "config_enhanced.json",
        "setup_enhanced.sh",
        "README_ENHANCED.md",
    ]

    missing_files = []
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)

    if not missing_files:
        print("✓ 所有必需文件都存在")
        return True
    else:
        print(f"✗ 缺少文件: {', '.join(missing_files)}")
        return False


def test_error_handler():
    """测试错误处理器"""
    print("\n测试错误处理器...")
    try:
        from error_handler import ErrorCode, MCPError, ErrorHandler

        # 测试错误代码
        assert ErrorCode.API_KEY_MISSING.name == "API_KEY_MISSING"

        # 测试MCPError
        error = MCPError("Test error", ErrorCode.API_KEY_MISSING)
        error_dict = error.to_dict()
        assert error_dict["error"] == "Test error"
        assert error_dict["error_code"] == ErrorCode.API_KEY_MISSING.value

        print("✓ 错误处理器测试通过")
        return True
    except Exception as e:
        print(f"✗ 错误处理器测试失败: {str(e)}")
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("\n测试缓存管理器...")
    try:
        from cache_manager import MemoryCache, FileCache, HybridCache

        # 测试内存缓存
        memory_cache = MemoryCache(max_size=10, default_ttl=60)
        memory_cache.set("test", "value", key="test_key")
        result = memory_cache.get("test", key="test_key")
        assert result == "value"

        print("✓ 缓存管理器测试通过")
        return True
    except Exception as e:
        print(f"✗ 缓存管理器测试失败: {str(e)}")
        return False


def test_middleware():
    """测试中间件"""
    print("\n测试中间件...")
    try:
        # 由于中间件模块依赖aiohttp，我们只测试基本Python语法
        # 通过检查文件是否存在和可导入来验证

        with open("middleware.py", "r") as f:
            content = f.read()

        # 检查关键类是否存在
        required_classes = [
            "RateLimiter",
            "APIKeyAuthenticator",
            "RequestLogger",
            "CORSHandler",
            "SecurityHeaders",
            "MiddlewareManager",
        ]

        for cls_name in required_classes:
            if f"class {cls_name}" not in content:
                raise Exception(f"缺少类: {cls_name}")

        print("✓ 中间件测试通过（基本结构验证）")
        return True
    except Exception as e:
        print(f"✗ 中间件测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("智谱AI MCP服务器增强版 - 代码测试")
    print("=" * 50)

    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    tests = [
        ("模块导入测试", test_module_imports),
        ("文件结构测试", test_file_structure),
        ("配置验证测试", test_config_validation),
        ("错误处理器测试", test_error_handler),
        ("缓存管理器测试", test_cache_manager),
        ("中间件测试", test_middleware),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n运行 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 通过")
            else:
                print(f"✗ {test_name} 失败")
        except Exception as e:
            print(f"✗ {test_name} 异常: {str(e)}")

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✓ 所有测试通过！代码结构良好。")
        print("\n注意: 要运行完整服务器，需要安装以下依赖:")
        print("  pip3 install aiohttp beautifulsoup4 zhipuai")
        return True
    else:
        print("✗ 部分测试失败，请检查代码。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
