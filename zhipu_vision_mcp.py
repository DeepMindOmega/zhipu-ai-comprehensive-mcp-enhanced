#!/usr/bin/env python3
"""
智谱AI Vision MCP Server
遵循 Model Context Protocol 规范的视觉模型服务器
"""

import asyncio
import json
import base64
from typing import Dict, Any, List
from aiohttp import web, WSMsgType
import logging
from zhipuai import ZhipuAI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuVisionMCP:
    def __init__(self, api_key: str):
        self.api_key = api_key
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
            "name": "zhipu-vision-mcp",
            "version": "1.0.0",
            "description": "智谱AI视觉模型MCP服务器",
            "models": [
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
            "endpoints": {
                "execute": {
                    "method": "POST",
                    "path": "/execute",
                    "description": "执行视觉模型推理",
                    "parameters": {
                        "model": {"type": "string", "required": True},
                        "image": {"type": "string", "required": True},  # base64 encoded
                        "prompt": {"type": "string", "required": False}
                    }
                }
            }
        }
        return web.json_response(capabilities)
    
    async def handle_execute(self, request):
        """处理执行请求"""
        try:
            data = await request.json()
            
            model = data.get("model", "glm-vision")
            image_data = data.get("image")  # base64编码的图像数据
            prompt = data.get("prompt", "请详细描述这张图片的内容")
            
            if not image_data:
                return web.json_response({
                    "error": "Missing image data",
                    "success": False
                }, status=400)
            
            # 解码图像数据
            if image_data.startswith("data:image"):
                # 移除data URL前缀
                image_data = image_data.split(",")[1]
            
            # 调用智谱AI视觉模型
            result = self.call_vision_model(model, image_data, prompt)
            
            return web.json_response({
                "success": True,
                "result": result,
                "model_used": model
            })
            
        except Exception as e:
            logger.error(f"Error processing vision request: {e}")
            return web.json_response({
                "error": str(e),
                "success": False
            }, status=500)
    
    def call_vision_model(self, model: str, image_base64: str, prompt: str) -> Dict[str, Any]:
        """调用智谱AI视觉模型"""
        try:
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
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            # 提取结果
            content = response.choices[0].message.content
            usage = response.usage if hasattr(response, 'usage') else None
            
            return {
                "text": content,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Error calling vision model: {e}")
            raise
    
    def create_app(self):
        """创建aiohttp应用"""
        app = web.Application()
        app.add_routes(self.routes)
        return app

async def main():
    """主函数"""
    # 从环境变量或配置文件获取API密钥
    import os
    api_key = os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("请设置 ZHIPU_API_KEY 环境变量")
        return
    
    vision_mcp = ZhipuVisionMCP(api_key)
    app = vision_mcp.create_app()
    
    # 运行服务器
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    
    print("智谱AI Vision MCP Server 已启动")
    print("能力查询: GET http://localhost:8000/capabilities")
    print("执行接口: POST http://localhost:8000/execute")
    
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
    except ImportError:
        print("请先安装 zhipuai 包: pip install zhipuai")
        exit(1)
    
    asyncio.run(main())