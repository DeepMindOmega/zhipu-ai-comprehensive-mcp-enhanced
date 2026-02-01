# 智谱AI Comprehensive MCP 服务器 (增强版)

这是一个功能全面的智谱AI MCP（Model Context Protocol）服务器，集成了多种AI能力，包括文本生成、网络搜索、网页分析、仓库分析和视觉理解等功能。

## 新版改进内容

### 🚀 核心改进

1. **配置验证系统** - 自动验证配置文件的完整性和有效性
2. **增强错误处理** - 统一的错误处理和友好的错误消息
3. **智能缓存机制** - 内存和文件混合缓存，减少API调用
4. **中间件系统** - 请求限流、身份验证、CORS支持、安全头部
5. **健康检查端点** - 监控服务器状态和性能指标
6. **缓存管理端点** - 查看和清理缓存数据

### 🔧 技术改进

- 代码结构优化和模块化设计
- 更详细的日志记录和错误追踪
- 支持配置热重载
- 更好的性能监控和统计

## 项目特性

### 功能特性
- **文本生成** - 使用智谱GLM-4模型生成高质量文本
- **网络搜索** - 智谱AI驱动的智能搜索功能（带缓存）
- **网页读取** - 自动抓取和分析网页内容，支持AI摘要（带缓存）
- **开源仓库分析** - 分析GitHub/GitLab仓库结构和内容（带缓存）
- **视觉理解** - 图像分析和理解能力
- **智能降级** - 在没有API密钥时提供基础功能
- **符合MCP规范** - 遵循标准的Model Context Protocol

### 支持的工具
- `web_search`: 联网搜索
- `web_reader`: 网页读取
- `repo_analyzer`: 开源仓库分析
- `vision_analyzer`: 视觉理解
- `text_generator`: 文本生成

## 新增端点

- `GET /capabilities` - 查询服务器能力
- `POST /execute` - 执行AI功能
- `GET /health` - 健康检查
- `GET /cache/stats` - 缓存统计信息
- `POST /cache/clear` - 清除缓存

## 安全特性

- 敏感配置信息通过 `.gitignore` 排除
- 支持配置文件和环境变量两种API密钥管理方式
- 请求频率限制防止滥用
- 可选的API密钥身份验证
- CORS支持和安全头部
- 明确的错误提示，区分需要API密钥的功能

## 安装和使用

### 快速安装

```bash
git clone https://github.com/DeepMindOmega/zhipu-ai-comprehensive-mcp.git
cd zhipu-ai-comprehensive-mcp
./setup_enhanced.sh
```

### 手动配置

1. 安装依赖：
   ```bash
   pip3 install -r requirements.txt
   ```
   
   或者使用项目自带的安装脚本：
   ```bash
   ./setup_enhanced.sh
   ```

2. 配置API密钥：
   直接编辑 `zhipu_comprehensive_config.json` 文件，将 `"输入你的智谱api insert your api here"` 替换为您的实际API密钥

3. 启动服务器（增强版）：
   ```bash
   ./start_enhanced.sh
   ```
   或者：
   ```bash
   python3 zhipu_comprehensive_mcp_enhanced_v2.py
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

### 健康检查
```bash
curl http://localhost:8000/health
```

### 缓存统计
```bash
curl http://localhost:8000/cache/stats
```

### 清除缓存
```bash
curl -X POST http://localhost:8000/cache/clear \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "web_search"
  }'
```

## 配置文件说明

增强版配置文件包含以下设置：

### 服务器配置
- `host`: 服务器主机地址
- `port`: 服务器端口
- `debug`: 调试模式
- `log_body`: 是否记录请求体
- `cache_dir`: 缓存目录
- `rate_limits`: 请求频率限制设置

### 智谱AI配置
- `api_key`: API密钥
- `default_model`: 默认模型
- `timeout`: 请求超时时间

### MCP服务配置
- `name`: 服务名称
- `version`: 服务版本
- `description`: 服务描述

### 功能开关
- `web_search`: 是否启用网页搜索
- `web_reader`: 是否启用网页读取
- `repo_analyzer`: 是否启用仓库分析
- `vision_analyzer`: 是否启用视觉分析
- `text_generator`: 是否启用文本生成

### 认证配置
- `require_auth`: 是否需要身份验证
- `api_keys`: 有效API密钥列表

### CORS配置
- `allowed_origins`: 允许的源地址

## 项目结构

```
zhipu-ai-comprehensive-mcp/
├── zhipu_comprehensive_mcp_enhanced_v2.py  # 增强版服务器主文件
├── config_validator.py                     # 配置验证模块
├── error_handler.py                         # 错误处理模块
├── cache_manager.py                         # 缓存管理模块
├── middleware.py                           # 中间件模块
├── config_enhanced.json                    # 增强版配置文件模板
├── setup_enhanced.sh                       # 增强版安装脚本
├── start_enhanced.sh                       # 增强版启动脚本
├── requirements.txt                        # 依赖文件
├── cache/                                  # 缓存目录
├── logs/                                   # 日志目录
├── zhipu_comprehensive_mcp.py              # 原始服务器文件
├── zhipu_comprehensive_mcp_enhanced.py    # 原增强版服务器文件
└── README.md                               # 项目说明
```

## 缓存系统

增强版引入了混合缓存系统：
- **内存缓存**: 快速访问热点数据
- **文件缓存**: 持久化存储，重启后仍可用

缓存策略：
- 网页搜索: 30分钟
- 网页读取: 1小时
- 仓库分析: 2小时

## 中间件功能

### 请求频率限制
- 每分钟请求数限制
- 每小时请求数限制
- 自动清理过期记录

### 身份验证（可选）
- 基于API密钥的身份验证
- 支持请求头或查询参数传递密钥
- 可配置启用/禁用

### CORS支持
- 可配置允许的源地址
- 支持预检请求处理

### 安全头部
- XSS保护
- 内容类型保护
- 点击劫持保护

## 性能监控

增强版提供多种性能监控功能：
- 请求统计
- 缓存命中率
- API使用情况
- 错误追踪

## 安全注意事项

- 请勿在代码中硬编码API密钥
- 定期轮换API密钥
- 确保配置文件不被提交到版本控制
- 使用HTTPS保护网络通信
- 使用最小权限原则配置API密钥
- 合理设置请求频率限制
- 定期清理缓存日志

## 故障排除

### 常见问题

1. **配置文件验证失败**
   - 检查JSON格式是否正确
   - 确认必填字段完整
   - 验证字段类型

2. **API调用失败**
   - 确认API密钥有效
   - 检查网络连接
   - 查看错误日志

3. **缓存问题**
   - 检查缓存目录权限
   - 清理过期缓存
   - 查看缓存统计

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

Copyright (c) 2024-present DeepMindOmega