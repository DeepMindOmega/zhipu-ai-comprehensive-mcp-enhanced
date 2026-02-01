# 智谱AI Comprehensive MCP 服务器

这是一个功能全面的智谱AI MCP（Model Context Protocol）服务器，集成了多种AI能力，包括文本生成、网络搜索、网页分析、仓库分析和视觉理解等功能。

## 项目特性

### 功能特性
- **文本生成** - 使用智谱GLM-4模型生成高质量文本
- **网络搜索** - 智谱AI驱动的智能搜索功能
- **网页读取** - 自动抓取和分析网页内容，支持AI摘要
- **开源仓库分析** - 分析GitHub/GitLab仓库结构和内容
- **视觉理解** - 图像分析和理解能力
- **智能降级** - 在没有API密钥时提供基础功能
- **符合MCP规范** - 遵循标准的Model Context Protocol

### 支持的工具
- `web_search`: 联网搜索
- `web_reader`: 网页读取
- `repo_analyzer`: 开源仓库分析
- `vision_analyzer`: 视觉理解
- `text_generator`: 文本生成

## 安全特性

- 敏感配置信息通过 `.gitignore` 排除
- 支持配置文件和环境变量两种API密钥管理方式
- 明确的错误提示，区分需要API密钥的功能

## 安装和使用

### 快速安装

```bash
git clone https://github.com/DeepMindOmega/zhipu-ai-comprehensive-mcp.git
cd zhipu-ai-comprehensive-mcp
./setup.sh
```

### 手动配置

1. 安装依赖：
   ```bash
   pip3 install zhipuai aiohttp beautifulsoup4
   ```
   
   或者使用项目自带的安装脚本：
   ```bash
   ./setup.sh
   ```

2. 配置API密钥：
   直接编辑 `zhipu_comprehensive_config.json` 文件，将 `"YOUR_ZHIPU_API_KEY_HERE"` 替换为您的实际API密钥

3. 启动服务器
   ```bash
   python3 zhipu_comprehensive_mcp_enhanced.py
   ```

## API使用示例

### 联网搜索
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "web_search",
    "params": {
      "query": "人工智能最新发展",
      "max_results": 5
    }
  }'
```

### 网页读取
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "web_reader",
    "params": {
      "url": "https://example.com/article",
      "summary": true
    }
  }'
```

### 文本生成
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "text_generator",
    "params": {
      "prompt": "写一段简短的欢迎词",
      "model": "glm-4"
    }
  }'
```

## API端点

- `GET /capabilities` - 查询服务器能力
- `POST /execute` - 执行AI功能

## 配置文件

配置文件包含以下设置：
- 服务器配置（主机、端口、调试模式）
- 智谱AI API配置（API密钥、默认模型、超时设置）
- MCP服务配置（名称、版本、描述）
- 功能开关（启用/禁用特定功能）

## 项目结构

```
zhipu/
├── zhipu_comprehensive_mcp.py          # 主服务器实现（综合性）
├── zhipu_comprehensive_mcp_enhanced.py # 增强版服务器实现（支持智能功能降级）
├── zhipu_comprehensive_config.json     # 配置文件（综合性）
├── config.template.json                # 配置文件模板
├── start_zhipu_comprehensive.sh        # 综合性服务器启动脚本
├── setup.sh                            # 一键安装脚本
├── test_all_functions.js               # 功能测试脚本
├── README.md                           # 项目说明
├── SECURITY.md                         # 安全说明
└── LICENSE                             # 许可证文件
```

## 安全注意事项

- 请勿在代码中硬编码API密钥
- 定期轮换API密钥
- 确保配置文件不被提交到版本控制
- 使用HTTPS保护网络通信
- 使用最小权限原则配置API密钥

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

Copyright (c) 2024-present DeepMindOmega