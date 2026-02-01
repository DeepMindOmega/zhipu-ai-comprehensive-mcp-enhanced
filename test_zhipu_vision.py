#!/usr/bin/env python3
"""
智谱AI Vision MCP Server 测试脚本
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
            return True
        else:
            print(f"✗ 能力查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接服务器失败: {e}")
        return False

def test_vision_api():
    """测试视觉API接口（使用示例图像数据）"""
    print("\n测试视觉API接口...")
    
    # 创建一个简单的测试图像数据 (这里是示例，实际使用时需要真实图像)
    # 由于我们没有真实的图像，这里只是测试API接口格式
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # 1x1像素透明PNG
    
    payload = {
        "model": "glm-vision",
        "image": test_image_data,
        "prompt": "这是一个测试图像，请忽略"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ 视觉API调用成功")
                return True
            else:
                print(f"✗ 视觉API调用失败: {result.get('error')}")
                return False
        else:
            print(f"✗ 视觉API请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 视觉API连接失败: {e}")
        print("   提示: 请确保服务器正在运行")
        return False

def main():
    """主测试函数"""
    print("智谱AI Vision MCP Server 测试")
    print("=" * 40)
    
    # 测试服务器是否运行
    cap_success = test_capabilities()
    vision_success = test_vision_api() if cap_success else False
    
    print("\n测试结果:")
    print(f"能力查询: {'✓ 通过' if cap_success else '✗ 失败'}")
    print(f"视觉API: {'✓ 通过' if vision_success else '✗ 失败'}")
    
    if cap_success and vision_success:
        print("\n✓ 所有测试通过!")
        print("服务器已准备就绪，可以通过以下方式使用:")
        print("  1. 获取能力: GET http://localhost:8000/capabilities")
        print("  2. 执行分析: POST http://localhost:8000/execute")
    else:
        print("\n✗ 测试未全部通过")
        print("请确保:")
        print("  1. 服务器正在运行 (使用 ./start_zhipu_vision.sh)")
        print("  2. 配置文件中设置了有效的API密钥")

if __name__ == "__main__":
    main()