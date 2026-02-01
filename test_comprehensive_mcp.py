#!/usr/bin/env python3
"""
智谱AI Comprehensive MCP Server 测试脚本
"""

import json
import requests
import base64
from pathlib import Path

def test_capabilities():
    """测试能力查询接口"""
    print("测试能力查询接口...")
    try:
        response = requests.get("http://localhost:8000/capabilities")
        if response.status_code == 200:
            capabilities = response.json()
            print("✓ 能力查询成功")
            print(f"  服务器名称: {capabilities.get('name')}")
            print(f"  版本: {capabilities.get('version')}")
            print(f"  描述: {capabilities.get('description')}")
            
            # 检查工具列表
            tools = capabilities.get('tools', [])
            print(f"  可用工具数量: {len(tools)}")
            for tool in tools:
                print(f"    - {tool['name']}: {tool['description']}")
            
            return True
        else:
            print(f"✗ 能力查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接服务器失败: {e}")
        return False

def test_web_search():
    """测试联网搜索功能"""
    print("\n测试联网搜索功能...")
    try:
        payload = {
            "tool": "web_search",
            "params": {
                "query": "智谱AI最新发展",
                "max_results": 2
            }
        }
        
        response = requests.post(
            "http://localhost:8000/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ 联网搜索功能调用成功")
                print(f"  工具使用: {result.get('tool_used')}")
                return True
            else:
                print(f"✗ 联网搜索功能调用失败: {result.get('error')}")
                return False
        else:
            print(f"✗ 联网搜索请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 联网搜索连接失败: {e}")
        print("   提示: 请确保服务器正在运行")
        return False

def test_web_reader():
    """测试网页读取功能"""
    print("\n测试网页读取功能...")
    try:
        payload = {
            "tool": "web_reader",
            "params": {
                "url": "https://httpbin.org/html",
                "summary": True
            }
        }
        
        response = requests.post(
            "http://localhost:8000/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ 网页读取功能调用成功")
                print(f"  工具使用: {result.get('tool_used')}")
                return True
            else:
                print(f"✗ 网页读取功能调用失败: {result.get('error')}")
                return False
        else:
            print(f"✗ 网页读取请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 网页读取连接失败: {e}")
        print("   提示: 请确保服务器正在运行")
        return False

def test_text_generation():
    """测试文本生成功能"""
    print("\n测试文本生成功能...")
    try:
        payload = {
            "tool": "text_generator",
            "params": {
                "prompt": "请简单介绍一下人工智能的发展历程，50字以内",
                "model": "glm-4"
            }
        }
        
        response = requests.post(
            "http://localhost:8000/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ 文本生成功能调用成功")
                print(f"  工具使用: {result.get('tool_used')}")
                return True
            else:
                print(f"✗ 文本生成功能调用失败: {result.get('error')}")
                return False
        else:
            print(f"✗ 文本生成请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 文本生成连接失败: {e}")
        print("   提示: 请确保服务器正在运行")
        return False

def main():
    """主测试函数"""
    print("智谱AI Comprehensive MCP Server 测试")
    print("=" * 50)
    
    # 测试服务器是否运行
    cap_success = test_capabilities()
    search_success = test_web_search() if cap_success else False
    reader_success = test_web_reader() if cap_success else False
    text_gen_success = test_text_generation() if cap_success else False
    
    print("\n测试结果:")
    print(f"能力查询: {'✓ 通过' if cap_success else '✗ 失败'}")
    print(f"联网搜索: {'✓ 通过' if search_success else '✗ 失败'}")
    print(f"网页读取: {'✓ 通过' if reader_success else '✗ 失败'}")
    print(f"文本生成: {'✓ 通过' if text_gen_success else '✗ 失败'}")
    
    total_passed = sum([cap_success, search_success, reader_success, text_gen_success])
    total_tests = 4
    
    print(f"\n总体结果: {total_passed}/{total_tests} 测试通过")
    
    if total_passed == total_tests:
        print("\n✓ 所有测试通过!")
        print("服务器已准备就绪，支持以下功能:")
        print("  1. 联网搜索 - web_search")
        print("  2. 网页读取 - web_reader")
        print("  3. 开源仓库分析 - repo_analyzer")
        print("  4. 视觉理解 - vision_analyzer")
        print("  5. 文本生成 - text_generator")
    else:
        print("\n✗ 部分测试未通过")
        print("请确保:")
        print("  1. 服务器正在运行 (使用 ./start_zhipu_comprehensive.sh)")
        print("  2. 配置文件中设置了有效的API密钥")
        print("  3. 网络连接正常")

if __name__ == "__main__":
    main()