#!/usr/bin/env python3
"""
智谱AI Enhanced Comprehensive MCP Server (改进版)
增强版综合性Model Context Protocol服务器，包含多种AI能力
支持在没有API密钥的情况下使用基础功能

改进内容:
1. 添加配置验证
2. 增强错误处理
3. 添加缓存机制
4. 实现中间件（认证、限流、日志）
5. 优化代码结构
"""

import asyncio
import json
import base64
import requests
import time
import sys
from typing import Dict, Any, List, Optional
from aiohttp import web, ClientSession
import logging
import os
import urllib.parse
from bs4 import BeautifulSoup

# 尝试导入智谱AI库
try:
    from zhipuai import ZhipuAI

    ZHIPU_AVAILABLE = True
except ImportError:
    ZHIPU_AVAILABLE = False

# 导入自定义模块
from config_validator import ConfigValidator
from error_handler import ErrorHandler, MCPError, ErrorCode, error_handler_decorator
from cache_manager import HybridCache, cache_decorator
from middleware import MiddlewareManager

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ZhipuComprehensiveEnhancedMCP:
    """增强版智谱AI综合性MCP服务器"""

    def __init__(self, config_file: str = "zhipu_comprehensive_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.api_key = self.config.get("zhipu", {}).get("api_key")
        self.client = None

        if self.api_key and ZHIPU_AVAILABLE:
            try:
                self.client = ZhipuAI(api_key=self.api_key)
                logger.info("智谱AI客户端初始化成功")
            except Exception as e:
                logger.warning(f"智谱AI客户端初始化失败: {str(e)}")

        # 初始化组件
        self.error_handler = ErrorHandler(logger)
        self.cache = HybridCache(
            cache_dir=self.config.get("server", {}).get("cache_dir", "cache"),
            memory_max_size=50,
            default_ttl=3600,  # 1小时缓存
        )
        self.middleware_manager = MiddlewareManager()
        self._configure_middleware()

        # 创建默认错误处理器实例
        self.default_error_handler = self.error_handler

        # 设置路由
        self.routes = web.RouteTableDef()
        self.setup_routes()

        logger.info("MCP服务器初始化完成")

    def _load_config(self) -> Dict[str, Any]:
        """加载并验证配置"""
        is_valid, errors, config = ConfigValidator.validate_config(self.config_file)

        if not is_valid:
            error_msg = "配置文件验证失败:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("配置文件验证通过")
        return config

    def _configure_middleware(self):
        """配置中间件"""
        # 配置请求频率限制
        server_config = self.config.get("server", {})
        rate_limits = server_config.get("rate_limits", {})
        self.middleware_manager.configure_rate_limiting(
            requests_per_minute=rate_limits.get("per_minute", 60),
            requests_per_hour=rate_limits.get("per_hour", 1000),
        )

        # 配置认证
        auth_config = self.config.get("auth", {})
        api_keys = auth_config.get("api_keys", [])
        require_auth = auth_config.get("require_auth", False)
        self.middleware_manager.configure_authentication(api_keys, require_auth)

        # 配置CORS
        cors_config = self.config.get("cors", {})
        allowed_origins = cors_config.get("allowed_origins", ["*"])
        self.middleware_manager.configure_cors(allowed_origins)

        # 配置日志
        self.middleware_manager.configure_logging(
            logger, log_body=server_config.get("log_body", False)
        )

    def setup_routes(self):
        """设置路由"""
        self.routes.get("/capabilities")(self.handle_capabilities)
        self.routes.get("/health")(self.handle_health)
        self.routes.post("/execute")(self.handle_execute)
        self.routes.get("/cache/stats")(self.handle_cache_stats)
        self.routes.post("/cache/clear")(self.handle_cache_clear)

    async def handle_capabilities(self, request: web.Request) -> web.Response:
        """处理能力查询请求"""
        capabilities = {
            "name": self.config.get("mcp", {}).get(
                "name", "zhipu-comprehensive-enhanced-mcp"
            ),
            "version": self.config.get("mcp", {}).get("version", "1.0.0"),
            "description": self.config.get("mcp", {}).get(
                "description", "智谱AI增强版综合性MCP服务器"
            ),
            "models": [
                {
                    "id": "glm-4",
                    "name": "GLM-4",
                    "description": "智谱AI大语言模型",
                    "capabilities": ["text_generation", "conversation", "analysis"],
                }
            ],
            "tools": [
                {
                    "name": "web_search",
                    "description": "智谱AI联网搜索",
                    "parameters": {
                        "query": {
                            "type": "string",
                            "required": True,
                            "description": "搜索查询",
                        },
                        "max_results": {
                            "type": "integer",
                            "required": False,
                            "default": 5,
                            "description": "最大结果数",
                        },
                    },
                },
                {
                    "name": "web_reader",
                    "description": "网页内容读取",
                    "parameters": {
                        "url": {
                            "type": "string",
                            "required": True,
                            "description": "网页URL",
                        },
                        "summary": {
                            "type": "boolean",
                            "required": False,
                            "default": False,
                            "description": "是否生成摘要",
                        },
                    },
                },
                {
                    "name": "repo_analyzer",
                    "description": "开源仓库分析",
                    "parameters": {
                        "repo_url": {
                            "type": "string",
                            "required": True,
                            "description": "仓库URL",
                        },
                        "analyze_readme": {
                            "type": "boolean",
                            "required": False,
                            "default": True,
                            "description": "是否分析README",
                        },
                        "analyze_structure": {
                            "type": "boolean",
                            "required": False,
                            "default": True,
                            "description": "是否分析结构",
                        },
                    },
                },
                {
                    "name": "vision_analyzer",
                    "description": "图像分析",
                    "parameters": {
                        "image": {
                            "type": "string",
                            "required": True,
                            "description": "图像数据(base64或URL)",
                        },
                        "prompt": {
                            "type": "string",
                            "required": False,
                            "default": "请详细描述这张图片的内容",
                        },
                    },
                },
            ],
            "endpoints": {
                "execute": {
                    "method": "POST",
                    "path": "/execute",
                    "description": "执行各种AI能力",
                    "parameters": {
                        "tool": {
                            "type": "string",
                            "required": True,
                            "description": "要使用的工具名称",
                        },
                        "params": {
                            "type": "object",
                            "required": True,
                            "description": "工具参数",
                        },
                    },
                }
            },
            "features": self.config.get("features", {}),
            "api_key_available": bool(self.api_key and self.client),
        }
        return web.json_response(capabilities)

    async def handle_health(self, request: web.Request) -> web.Response:
        """健康检查端点"""
        health_status = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "api_key_available": bool(self.api_key and self.client),
            "features_enabled": self.config.get("features", {}),
            "cache_stats": self.cache.stats(),
        }
        return web.json_response(health_status)

    async def handle_cache_stats(self, request: web.Request) -> web.Response:
        """获取缓存统计信息"""
        return web.json_response(self.cache.stats())

    async def handle_cache_clear(self, request: web.Request) -> web.Response:
        """清除缓存"""
        data = await request.json()
        prefix_filter = data.get("prefix")
        self.cache.clear(prefix_filter)

        return web.json_response(
            {
                "success": True,
                "message": "Cache cleared successfully",
                "filter": prefix_filter,
            }
        )

    async def handle_execute(self, request: web.Request) -> web.Response:
        """处理执行请求"""
        data = await request.json()

        tool_name = data.get("tool")
        params = data.get("params", {})

        if not tool_name:
            raise MCPError(
                "Missing tool name",
                ErrorCode.MISSING_PARAMETER,
                {"received": list(data.keys())},
            )

        # 检查工具是否被启用
        features = self.config.get("features", {})
        if not features.get(tool_name, True):
            raise MCPError(
                f"Tool '{tool_name}' is disabled",
                ErrorCode.INVALID_PARAMETER,
                {"tool": tool_name},
            )

        # 检查是否需要API密钥
        requires_api_key = tool_name in [
            "web_search",
            "repo_analyzer",
            "vision_analyzer",
            "text_generation",
        ]
        if requires_api_key and not self.client:
            raise MCPError(
                f"Tool '{tool_name}' requires a valid API key",
                ErrorCode.API_KEY_MISSING,
                {"tool": tool_name},
            )

        # 根据工具名称执行相应功能
        tool_functions = {
            "web_search": self.web_search,
            "web_reader": self.web_reader,
            "repo_analyzer": self.repo_analyzer,
            "vision_analyzer": self.vision_analyzer,
            "text_generator": self.text_generation,
        }

        if tool_name not in tool_functions:
            raise MCPError(
                f"Unknown tool: {tool_name}",
                ErrorCode.INVALID_PARAMETER,
                {"available_tools": list(tool_functions.keys())},
            )

        # 执行工具函数
        result = await tool_functions[tool_name](**params)

        return web.json_response(
            {
                "success": True,
                "result": result,
                "tool_used": tool_name,
                "timestamp": int(time.time()),
            }
        )

    async def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """智谱AI联网搜索功能"""
        # 检查缓存
        cached_result = self.cache.get("web_search", query, max_results)
        if cached_result:
            logger.info(f"Using cached result for query: {query}")
            return cached_result

        if not self.client:
            raise MCPError(
                "Web search requires a valid API key", ErrorCode.API_KEY_MISSING
            )

        try:
            messages = [
                {
                    "role": "user",
                    "content": f"请帮我搜索关于 '{query}' 的信息，并提供最新的结果。",
                }
            ]

            response = self.client.chat.completions.create(
                model="glm-4", messages=messages, max_tokens=2000, temperature=0.7
            )

            usage_info = self._extract_usage_info(response)

            result = {
                "query": query,
                "results_count": max_results,
                "answer": response.choices[0].message.content,
                "usage": usage_info,
            }

            # 缓存结果
            self.cache.set(
                "web_search", result, ttl=1800, query=query, max_results=max_results
            )

            return result

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise MCPError(
                "Web search failed",
                ErrorCode.WEB_SEARCH_FAILED,
                {"query": query},
                original_exception=e,
            )

    async def web_reader(self, url: str, summary: bool = False) -> Dict[str, Any]:
        """网页内容读取功能"""
        # 检查缓存
        cache_key = f"{url}:{summary}"
        cached_result = self.cache.get("web_reader", cache_key)
        if cached_result:
            logger.info(f"Using cached result for URL: {url}")
            return cached_result
        try:
            # 获取网页内容
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            async with ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    content = await response.text()

            # 解析HTML内容
            soup = BeautifulSoup(content, "html.parser")

            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()

            # 提取主要内容
            title = soup.title.string if soup.title else "无标题"
            text_content = soup.get_text()

            # 清理文本
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = " ".join(chunk for chunk in chunks if chunk)

            if summary and self.client:
                # 使用智谱AI生成摘要
                messages = [
                    {
                        "role": "user",
                        "content": f"请对以下网页内容进行摘要：\n\n{title}\n\n{text_content[:4000]}...",
                    }
                ]

                summary_response = self.client.chat.completions.create(
                    model="glm-4", messages=messages, max_tokens=1000, temperature=0.5
                )

                result = {
                    "url": url,
                    "title": title,
                    "summary": summary_response.choices[0].message.content,
                    "original_length": len(text_content),
                    "summary_length": len(summary_response.choices[0].message.content),
                    "usage": self._extract_usage_info(summary_response),
                }

                # 缓存结果
                self.cache.set("web_reader", result, ttl=3600, cache_key=cache_key)

                return result
            else:
                # 返回基本的网页内容
                result = {
                    "url": url,
                    "title": title,
                    "content": text_content[:10000],  # 截断长内容
                    "length": len(text_content),
                    "summary_provided": False,
                }

                # 缓存结果
                self.cache.set("web_reader", result, ttl=3600, cache_key=cache_key)

                return result

        except Exception as e:
            logger.error(f"Web reader error: {str(e)}")
            raise MCPError(
                "Failed to read web content",
                ErrorCode.WEB_CONTENT_NOT_ACCESSIBLE,
                {"url": url},
                original_exception=e,
            )

    async def repo_analyzer(
        self, repo_url: str, analyze_readme: bool = True, analyze_structure: bool = True
    ) -> Dict[str, Any]:
        """开源仓库分析功能"""
        # 检查缓存
        cache_key = f"{repo_url}:{analyze_readme}:{analyze_structure}"
        cached_result = self.cache.get("repo_analyzer", cache_key)
        if cached_result:
            logger.info(f"Using cached result for repository: {repo_url}")
            return cached_result
        try:
            # 解析仓库URL
            parsed_url = urllib.parse.urlparse(repo_url)
            path_parts = parsed_url.path.strip("/").split("/")

            if len(path_parts) < 2:
                raise ValueError("Invalid repository URL")

            owner = path_parts[0]
            repo = path_parts[1]

            analysis_result = {
                "repository": f"{owner}/{repo}",
                "url": repo_url,
                "analysis": {},
            }

            if analyze_readme:
                # 获取README内容
                readme_urls = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/readme.md",
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
                    # 使用智谱AI分析README
                    messages = [
                        {
                            "role": "user",
                            "content": f"请分析以下开源仓库的README文件，并提供关键信息：\n\n{readme_content[:4000]}",
                        }
                    ]

                    analysis_response = self.client.chat.completions.create(
                        model="glm-4",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.5,
                    )

                    analysis_result["analysis"]["readme"] = {
                        "summary": analysis_response.choices[0].message.content,
                        "has_readme": True,
                        "usage": self._extract_usage_info(analysis_response),
                    }
                else:
                    analysis_result["analysis"]["readme"] = {
                        "summary": "未找到README文件或API密钥不可用",
                        "has_readme": readme_content is not None,
                    }

            if analyze_structure and self.client:
                # 使用智谱AI生成技术栈分析
                messages = [
                    {
                        "role": "user",
                        "content": f"根据仓库名称和常见的项目结构，请分析 {owner}/{repo} 可能使用的技术栈和架构特点。",
                    }
                ]

                structure_response = self.client.chat.completions.create(
                    model="glm-4", messages=messages, max_tokens=800, temperature=0.6
                )

                analysis_result["analysis"]["structure"] = {
                    "summary": structure_response.choices[0].message.content,
                    "type": "ai_analyzed",
                    "usage": self._extract_usage_info(structure_response),
                }
            else:
                analysis_result["analysis"]["structure"] = {
                    "summary": f"仓库 {owner}/{repo} 的基本结构信息",
                    "type": "basic_info_only",
                }

            # 缓存结果
            self.cache.set(
                "repo_analyzer", analysis_result, ttl=7200, cache_key=cache_key
            )

            return analysis_result

        except Exception as e:
            logger.error(f"Repo analyzer error: {str(e)}")
            raise MCPError(
                "Repository analysis failed",
                ErrorCode.REPOSITORY_NOT_FOUND,
                {"repo_url": repo_url},
                original_exception=e,
            )

    async def vision_analyzer(
        self, image_data: str, prompt: str = "请详细描述这张图片的内容"
    ) -> Dict[str, Any]:
        """视觉分析功能"""
        if not self.client:
            raise MCPError(
                "Vision analysis requires a valid API key", ErrorCode.API_KEY_MISSING
            )

        try:
            # 处理图像数据（如果是data URL格式，提取base64部分）
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                    ],
                }
            ]

            # 调用API
            response = self.client.chat.completions.create(
                model="glm-vision", messages=messages, max_tokens=2000, temperature=0.7
            )

            return {
                "analysis": response.choices[0].message.content,
                "usage": self._extract_usage_info(response),
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Vision analyzer error: {str(e)}")
            raise MCPError(
                "Image processing failed",
                ErrorCode.IMAGE_PROCESSING_FAILED,
                original_exception=e,
            )

    async def text_generation(
        self, prompt: str, model: str = "glm-4"
    ) -> Dict[str, Any]:
        """文本生成功能"""
        if not self.client:
            raise MCPError(
                "Text generation requires a valid API key", ErrorCode.API_KEY_MISSING
            )

        try:
            messages = [{"role": "user", "content": prompt}]

            response = self.client.chat.completions.create(
                model=model, messages=messages, max_tokens=2000, temperature=0.7
            )

            return {
                "text": response.choices[0].message.content,
                "usage": self._extract_usage_info(response),
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Text generation error: {str(e)}")
            raise MCPError(
                "Text generation failed",
                ErrorCode.TEXT_GENERATION_FAILED,
                original_exception=e,
            )

    def _extract_usage_info(self, response) -> Optional[Dict[str, Any]]:
        """提取API使用信息"""
        if not hasattr(response, "usage") or response.usage is None:
            return None

        usage_dict = {}
        if hasattr(response.usage, "prompt_tokens"):
            usage_dict["prompt_tokens"] = response.usage.prompt_tokens
        if hasattr(response.usage, "completion_tokens"):
            usage_dict["completion_tokens"] = response.usage.completion_tokens
        if hasattr(response.usage, "total_tokens"):
            usage_dict["total_tokens"] = response.usage.total_tokens

        return usage_dict


async def main():
    """主函数"""
    # 从环境变量或配置文件获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    config_file = "zhipu_comprehensive_config.json"

    # 如果环境变量中没有API密钥，尝试从命令行参数获取
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    # 创建并配置服务器
    try:
        mcp_server = ZhipuComprehensiveEnhancedMCP(config_file)
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {str(e)}")
        return

    # 创建应用
    app = web.Application()
    app.add_routes(mcp_server.routes)

    # 添加中间件
    app.middlewares.append(mcp_server.middleware_manager.create_middleware())

    # 获取服务器配置
    server_config = mcp_server.config.get("server", {})
    host = server_config.get("host", "localhost")
    port = server_config.get("port", 8000)

    logger.info(f"Starting MCP server on {host}:{port}")

    # 启动服务器
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    asyncio.run(main())
