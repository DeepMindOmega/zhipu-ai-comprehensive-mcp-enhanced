import requests
import json
import time

def test_zhipu_functions():
    base_url = "http://localhost:8000"
    
    print("开始测试智谱AI MCP服务器的所有功能...\n")
    
    # 测试服务器连接
    try:
        response = requests.get(f"{base_url}/capabilities", timeout=10)
        if response.status_code == 200:
            capabilities = response.json()
            print(f"✓ 服务器连接成功")
            print(f"  服务器: {capabilities['name']}")
            print(f"  版本: {capabilities['version']}")
            print(f"  描述: {capabilities['description']}\n")
        else:
            print(f"✗ 服务器连接失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ 服务器连接失败: {str(e)}")
        return
    
    # 测试文本生成
    print("1. 测试文本生成功能...")
    try:
        payload = {
            "tool": "text_generator",
            "params": {
                "prompt": "简要介绍人工智能的发展历程，不超过100字",
                "model": "glm-4"
            }
        }
        response = requests.post(f"{base_url}/execute", json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            print(f"  ✓ 文本生成成功")
            print(f"  结果长度: {len(result.get('result', ''))} 字符")
        else:
            print(f"  ⚠ 文本生成返回错误: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ✗ 文本生成出错: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试网页分析
    print("2. 测试网页分析功能...")
    try:
        payload = {
            "tool": "web_reader",
            "params": {
                "url": "https://www.baidu.com",
                "summary": True
            }
        }
        response = requests.post(f"{base_url}/execute", json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            print(f"  ✓ 网页分析成功")
            print(f"  内容长度: {len(result.get('result', ''))} 字符")
        else:
            print(f"  ⚠ 网页分析返回错误: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ✗ 网页分析出错: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试搜索功能
    print("3. 测试搜索功能...")
    try:
        payload = {
            "tool": "web_search",
            "params": {
                "query": "人工智能发展趋势",
                "max_results": 2
            }
        }
        response = requests.post(f"{base_url}/execute", json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            print(f"  ✓ 搜索功能成功")
            results = result.get('result', [])
            print(f"  返回结果数: {len(results)}")
        else:
            print(f"  ⚠ 搜索功能返回错误: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ✗ 搜索功能出错: {str(e)}")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    test_zhipu_functions()