# 智谱AI Comprehensive MCP Server - 项目概述

## 项目简介
这是一个功能全面的智谱AI MCP（Model Context Protocol）服务器，集成了多种AI能力，包括联网搜索、网页读取、开源仓库分析和视觉理解等。

## 核心功能

### 1. 联网搜索 (Web Search)
- 智谱AI驱动的智能搜索
- 支持多结果返回
- 实时信息获取

### 2. 网页读取 (Web Reader)
- 自动抓取网页内容
- HTML解析和清理
- 内容摘要生成

### 3. 开源仓库分析 (Repo Analyzer)
- GitHub/GitLab仓库分析
- README文件解析
- 项目结构预测

### 4. 视觉理解 (Vision Analyzer)
- 图像内容分析
- 物体识别
- 场景理解

### 5. 文本生成 (Text Generator)
- 基于GLM-4模型
- 高质量文本生成
- 多种应用场景

## 技术架构

### 依赖包
- `zhipuai`: 智谱AI官方SDK
- `aiohttp`: 异步HTTP服务器框架
- `beautifulsoup4`: HTML解析库

### 服务端口
- 默认端口: 8000
- 协议: HTTP REST API

### API设计
- 符合MCP规范
- 统一的执行接口
- 灵活的参数传递

## 文件结构
```
zhipu_comprehensive_mcp/
├── zhipu_comprehensive_mcp.py     # 主服务器实现
├── zhipu_comprehensive_config.json # 配置文件
├── start_zhipu_comprehensive.sh    # 启动脚本
├── ZHIPU_COMPREHENSIVE_MCP_README.md # 使用说明
├── test_comprehensive_mcp.py       # 测试脚本
└── ZHIPU_PROJECT_SUMMARY.md        # 项目概述
```

## 安装部署

### 1. 安装依赖
```bash
pip install zhipuai aiohttp beautifulsoup4
```

### 2. 配置API密钥
- 获取智谱AI API密钥
- 更新 `zhipu_comprehensive_config.json`

### 3. 启动服务
```bash
./start_zhipu_comprehensive.sh
```

## 使用示例

### 联网搜索
```json
{
  "tool": "web_search",
  "params": {
    "query": "人工智能最新发展",
    "max_results": 5
  }
}
```

### 网页读取
```json
{
  "tool": "web_reader",
  "params": {
    "url": "https://example.com/article",
    "summary": true
  }
}
```

### 仓库分析
```json
{
  "tool": "repo_analyzer",
  "params": {
    "repo_url": "https://github.com/user/repo",
    "analyze_readme": true
  }
}
```

### 视觉分析
```json
{
  "tool": "vision_analyzer",
  "params": {
    "image": "base64_encoded_image",
    "prompt": "描述图片内容"
  }
}
```

## 扩展性

此服务器设计为高度可扩展:
- 新增工具只需添加处理函数
- 统一接口简化集成
- 模块化架构便于维护

## 优势

1. **多功能集成**: 一站式解决多种AI需求
2. **标准化接口**: 符合MCP规范
3. **易于使用**: 统一的API调用方式
4. **灵活配置**: 支持多种参数定制
5. **实时能力**: 提供最新的信息获取

## 应用场景

- 智能助手开发
- 数据分析工具
- 内容生成应用
- 研究辅助工具
- 自动化工作流

## 维护

- 定期更新依赖包
- 监控API使用量
- 优化性能表现
- 扩展新功能模块