#!/usr/bin/env python3
"""
智谱AI Enhanced Comprehensive MCP Server
增强版综合性Model Context Protocol服务器，包含多种AI能力
支持在没有API密钥的情况下使用基础功能
"""

import asyncio
import json
import base64
import requests
from typing import Dict, Any, List
from aiohttp import web, ClientSession
import logging
from zhipuai import ZhipuAI
import urllib.parse
from bs4 import BeautifulSoup
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuComprehensiveEnhancedMCP:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = ZhipuAI(api_key=api_key)
        self.routes = web.RouteTableDef()
        self.setup_routes()
        
    def setup_routes(self):
        """设置路由"""
        self.routes.post("/execute")(self.handle_execute)
        self.routes.get("/capabilities")(self.handle_capabilities)
        
    async def handle_capabilities(self, request):
        """处理能力查询请求"""
        capabilities = {
            "name": "zhipu-comprehensive-enhanced-mcp",
            "version": "1.0.0",
            "description": "智谱AI增强版综合性MCP服务器，提供多种AI能力",
            "models": [
                {
                    "id": "glm-4",
                    "name": "GLM-4",
                    "description": "智谱AI大语言模型",
                    "capabilities": [
                        "text_generation",
                        "question_answering",
                        "summarization",
                        "translation"
                    ]
                },
                {
                    "id": "glm-vision",
                    "name": "GLM Vision",
                    "description": "智谱AI视觉理解模型",
                    "capabilities": [
                        "image_analysis",
                        "object_detection",
                        "scene_understanding",
                        "text_in_image_extraction"
                    ],
                    "input_types": ["image/jpeg", "image/png", "image/webp"],
                    "max_input_size": "10MB"
                }
            ],
            "tools": [
                {
                    "name": "web_search",
                    "description": "智谱AI联网搜索工具（需要API密钥）",
                    "parameters": {
                        "query": {"type": "string", "required": True, "description": "搜索查询"},
                        "max_results": {"type": "integer", "required": False, "default": 5}
                    }
                },
                {
                    "name": "web_reader",
                    "description": "网页内容读取工具（无需API密钥，可选AI摘要）",
                    "parameters": {
                        "url": {"type": "string", "required": True, "description": "网页URL"},
                        "summary": {"type": "boolean", "required": False, "default": False}
                    }
                },
                {
                    "name": "repo_analyzer",
                    "description": "开源仓库分析工具（需要API密钥）",
                    "parameters": {
                        "repo_url": {"type": "string", "required": True, "description": "仓库URL (GitHub/GitLab)"},
                        "analyze_readme": {"type": "boolean", "required": False, "default": True},
                        "analyze_structure": {"type": "boolean", "required": False, "default": True}
                    }
                },
                {
                    "name": "vision_analyzer",
                    "description": "图像分析工具（需要API密钥）",
                    "parameters": {
                        "image": {"type": "string", "required": True, "description": "base64编码的图像"},
                        "prompt": {"type": "string", "required": False, "default": "请详细描述这张图片的内容"}
                    }
                }
            ],
            "endpoints": {
                "execute": {
                    "method": "POST",
                    "path": "/execute",
                    "description": "执行各种AI能力",
                    "parameters": {
                        "tool": {"type": "string", "required": True, "description": "要使用的工具名称"},
                        "params": {"type": "object", "required": True, "description": "工具参数"}
                    }
                }
            }
        }
        return web.json_response(capabilities)
    
    async def handle_execute(self, request):
        """处理执行请求"""
        try:
            data = await request.json()
            
            tool_name = data.get("tool")
            params = data.get("params", {})
            
            if not tool_name:
                return web.json_response({
                    "error": "Missing tool name",
                    "success": False
                }, status=400)
            
            # 检查是否需要API密钥
            requires_api_key = tool_name in ["web_search", "repo_analyzer", "vision_analyzer", "text_generator"]
            if requires_api_key and not self.client:
                return web.json_response({
                    "error": f"Tool '{tool_name}' requires a valid API key",
                    "success": False
                }, status=401)
            
            # 根据工具名称执行相应功能
            if tool_name == "web_search":
                result = await self.web_search(params.get("query"), params.get("max_results", 5))
            elif tool_name == "web_reader":
                result = await self.web_reader(params.get("url"), params.get("summary", False))
            elif tool_name == "repo_analyzer":
                result = await self.repo_analyzer(
                    params.get("repo_url"),
                    params.get("analyze_readme", True),
                    params.get("analyze_structure", True)
                )
            elif tool_name == "vision_analyzer":
                result = await self.vision_analyzer(
                    params.get("image"),
                    params.get("prompt", "请详细描述这张图片的内容")
                )
            elif tool_name == "text_generator":
                result = await self.text_generation(
                    params.get("prompt"),
                    params.get("model", "glm-4")
                )
            else:
                return web.json_response({
                    "error": f"Unknown tool: {tool_name}",
                    "success": False
                }, status=400)
            
            return web.json_response({
                "success": True,
                "result": result,
                "tool_used": tool_name
            })
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.json_response({
                "error": str(e),
                "success": False
            }, status=500)
    
    async def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """智谱AI联网搜索功能"""
        try:
            # 使用智谱AI的搜索能力
            messages = [
                {
                    "role": "user",
                    "content": f"请帮我搜索关于 '{query}' 的信息，并提供最新的结果。"
                }
            ]
            
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage is not None:
                # 将CompletionUsage对象转换为字典
                usage_dict = {}
                if hasattr(response.usage, 'prompt_tokens'):
                    usage_dict['prompt_tokens'] = response.usage.prompt_tokens
                if hasattr(response.usage, 'completion_tokens'):
                    usage_dict['completion_tokens'] = response.usage.completion_tokens
                if hasattr(response.usage, 'total_tokens'):
                    usage_dict['total_tokens'] = response.usage.total_tokens
                usage_info = usage_dict
            
            return {
                "query": query,
                "results_count": max_results,
                "answer": response.choices[0].message.content,
                "usage": usage_info
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def web_reader(self, url: str, summary: bool = False) -> Dict[str, Any]:
        """网页内容读取功能"""
        try:
            # 获取网页内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    content = await response.text()
            
            # 解析HTML内容
            soup = BeautifulSoup(content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取主要内容
            title = soup.title.string if soup.title else "无标题"
            text_content = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            if summary and self.client:
                # 使用智谱AI生成摘要（如果API密钥可用）
                messages = [
                    {
                        "role": "user",
                        "content": f"请对以下网页内容进行摘要：\n\n{title}\n\n{text_content[:4000]}..."
                    }
                ]
                
                summary_response = self.client.chat.completions.create(
                    model="glm-4",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.5
                )
                
                return {
                    "url": url,
                    "title": title,
                    "summary": summary_response.choices[0].message.content,
                    "original_length": len(text_content),
                    "summary_length": len(summary_response.choices[0].message.content)
                }
            else:
                # 返回基本的网页内容（不摘要）
                return {
                    "url": url,
                    "title": title,
                    "content": text_content[:10000],  # 截断长内容
                    "length": len(text_content),
                    "summary_provided": False
                }
                
        except Exception as e:
            logger.error(f"Web reader error: {e}")
            raise
    
    async def repo_analyzer(self, repo_url: str, analyze_readme: bool = True, analyze_structure: bool = True) -> Dict[str, Any]:
        """开源仓库分析功能"""
        try:
            # 解析仓库URL
            parsed_url = urllib.parse.urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise ValueError("Invalid repository URL")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            analysis_result = {
                "repository": f"{owner}/{repo}",
                "url": repo_url,
                "analysis": {}
            }
            
            if analyze_readme:
                # 获取README内容
                readme_urls = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/readme.md"
                ]
                
                readme_content = None
                for readme_url in readme_urls:
                    try:
                        async with ClientSession() as session:
                            async with session.get(readme_url) as response:
                                if response.status == 200:
                                    readme_content = await response.text()
                                    break
                    except:
                        continue
                
                if readme_content and self.client:
                    # 使用智谱AI分析README（如果API密钥可用）
                    messages = [
                        {
                            "role": "user",
                            "content": f"请分析以下开源仓库的README文件，并提供关键信息：\n\n{readme_content[:4000]}"
                        }
                    ]
                    
                    analysis_response = self.client.chat.completions.create(
                        model="glm-4",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.5
                    )
                    
                    analysis_result["analysis"]["readme"] = {
                        "summary": analysis_response.choices[0].message.content,
                        "has_readme": True
                    }
                else:
                    analysis_result["analysis"]["readme"] = {
                        "summary": "未找到README文件或API密钥不可用",
                        "has_readme": readme_content is not None
                    }
            
            if analyze_structure and self.client:
                # 使用智谱AI生成技术栈分析（如果API密钥可用）
                messages = [
                    {
                        "role": "user",
                        "content": f"根据仓库名称和常见的项目结构，请分析 {owner}/{repo} 可能使用的技术栈和架构特点。"
                    }
                ]
                
                structure_response = self.client.chat.completions.create(
                    model="glm-4",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.6
                )
                
                analysis_result["analysis"]["structure"] = {
                    "summary": structure_response.choices[0].message.content,
                    "type": "ai_analyzed"
                }
            else:
                analysis_result["analysis"]["structure"] = {
                    "summary": f"仓库 {owner}/{repo} 的基本结构信息",
                    "type": "basic_info_only"
                }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Repo analyzer error: {e}")
            raise
    
    async def vision_analyzer(self, image_data: str, prompt: str) -> Dict[str, Any]:
        """视觉分析功能"""
        try:
            # 处理图像数据（如果是data URL格式，提取base64部分）
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用API
            response = self.client.chat.completions.create(
                model="glm-vision",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage is not None:
                # 将CompletionUsage对象转换为字典
                usage_dict = {}
                if hasattr(response.usage, 'prompt_tokens'):
                    usage_dict['prompt_tokens'] = response.usage.prompt_tokens
                if hasattr(response.usage, 'completion_tokens'):
                    usage_dict['completion_tokens'] = response.usage.completion_tokens
                if hasattr(response.usage, 'total_tokens'):
                    usage_dict['total_tokens'] = response.usage.total_tokens
                usage_info = usage_dict
            
            return {
                "analysis": response.choices[0].message.content,
                "usage": usage_info,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Vision analyzer error: {e}")
            raise
    
    async def text_generation(self, prompt: str, model: str = "glm-4") -> Dict[str, Any]:
        """文本生成功能"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage is not None:
                # 将CompletionUsage对象转换为字典
                usage_dict = {}
                if hasattr(response.usage, 'prompt_tokens'):
                    usage_dict['prompt_tokens'] = response.usage.prompt_tokens
                if hasattr(response.usage, 'completion_tokens'):
                    usage_dict['completion_tokens'] = response.usage.completion_tokens
                if hasattr(response.usage, 'total_tokens'):
                    usage_dict['total_tokens'] = response.usage.total_tokens
                usage_info = usage_dict
            
            return {
                "text": response.choices[0].message.content,
                "usage": usage_info,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            raise

async def main():
    """主函数"""
    # 从环境变量或配置文件获取API密钥
    import os
    import json
    
    api_key = os.getenv("ZHIPU_API_KEY")
    
    # 如果环境变量中没有API密钥，则尝试从配置文件读取
    if not api_key:
        config_file = "zhipu_comprehensive_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get("zhipu", {}).get("api_key")
            except Exception as e:
                print(f"读取配置文件时出错: {e}")
    
    mcp_server = ZhipuComprehensiveEnhancedMCP(api_key)
    app = web.Application()
    app.add_routes(mcp_server.routes)
    
    # 运行服务器
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    
    print("智谱AI Enhanced Comprehensive MCP Server 已启动")
    print(f"API密钥状态: {'已配置' if api_key else '未配置'}")
    print("能力查询: GET http://localhost:8000/capabilities")
    print("执行接口: POST http://localhost:8000/execute")
    print("\n支持的工具:")
    print("- web_search: 联网搜索（需要API密钥）")
    print("- web_reader: 网页读取（无需API密钥，摘要功能需要API密钥）")
    print("- repo_analyzer: 开源仓库分析（需要API密钥）")
    print("- vision_analyzer: 视觉理解（需要API密钥）")
    print("- text_generator: 文本生成（需要API密钥）")
    
    # 保持服务器运行
    try:
        await asyncio.Future()  # 永远等待
    except KeyboardInterrupt:
        print("服务器关闭")
        await runner.cleanup()

if __name__ == "__main__":
    # 检查是否安装了必要的包
    try:
        import zhipuai
        import aiohttp
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请安装所需依赖: pip install zhipuai aiohttp beautifulsoup4")
        exit(1)
    
    asyncio.run(main())