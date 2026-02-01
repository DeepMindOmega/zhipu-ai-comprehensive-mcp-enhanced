# 智谱AI Comprehensive MCP Server

这是一个功能全面的Model Context Protocol服务器，集成了智谱AI的多种能力，包括联网搜索、网页读取、开源仓库分析和视觉理解等。

## 功能特性

- **联网搜索**: 智谱AI驱动的智能搜索功能
- **网页读取**: 自动抓取和分析网页内容
- **开源仓库分析**: 分析GitHub/GitLab仓库结构和内容
- **视觉理解**: 图像分析和理解能力
- **文本生成**: 基于GLM-4模型的文本生成
- **符合MCP规范**: 遵循标准的Model Context Protocol

## 安装依赖

```bash
pip install zhipuai aiohttp beautifulsoup4
```

## 配置

1. 获取智谱AI API密钥：访问 [https://bigmodel.cn](https://bigmodel.cn) 注册并获取API密钥
2. 编辑 `zhipu_comprehensive_config.json` 文件，替换 `YOUR_ZHIPU_API_KEY_HERE` 为实际的API密钥

## 启动服务器

```bash
./start_zhipu_comprehensive.sh
```

服务器将在 `http://localhost:8000` 上运行。

## API接口

### 获取服务器能力
```
GET http://localhost:8000/capabilities
```

返回服务器支持的所有模型和工具。

### 执行功能
```
POST http://localhost:8000/execute
Content-Type: application/json

{
  "tool": "tool_name",
  "params": {
    // 工具特定的参数
  }
}
```

## 支持的工具

### 1. 联网搜索 (web_search)
搜索互联网上的信息：

```json
{
  "tool": "web_search",
  "params": {
    "query": "人工智能最新发展",
    "max_results": 5
  }
}
```

### 2. 网页读取 (web_reader)
读取和分析网页内容：

```json
{
  "tool": "web_reader",
  "params": {
    "url": "https://example.com/article",
    "summary": true
  }
}
```

### 3. 开源仓库分析 (repo_analyzer)
分析GitHub/GitLab仓库：

```json
{
  "tool": "repo_analyzer",
  "params": {
    "repo_url": "https://github.com/user/repo",
    "analyze_readme": true,
    "analyze_structure": true
  }
}
```

### 4. 视觉分析 (vision_analyzer)
分析图像内容：

```json
{
  "tool": "vision_analyzer",
  "params": {
    "image": "base64_encoded_image_data",
    "prompt": "请描述这张图片的内容"
  }
}
```

### 5. 文本生成 (text_generator)
生成文本内容：

```json
{
  "tool": "text_generator",
  "params": {
    "prompt": "写一篇关于气候变化的文章",
    "model": "glm-4"
  }
}
```

## 响应格式

所有工具的响应都遵循以下格式：

```json
{
  "success": true,
  "result": {
    // 工具特定的结果
  },
  "tool_used": "tool_name"
}
```

## 使用示例

### JavaScript示例
```javascript
// 执行联网搜索
fetch('http://localhost:8000/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool: 'web_search',
    params: {
      query: '智谱AI最新动态',
      max_results: 3
    }
  })
})
.then(response => response.json())
.then(data => console.log(data.result));

// 分析网页
fetch('http://localhost:8000/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool: 'web_reader',
    params: {
      url: 'https://bigmodel.cn',
      summary: true
    }
  })
})
.then(response => response.json())
.then(data => console.log(data.result.summary));
```

### Python示例
```python
import requests
import json

# 分析GitHub仓库
response = requests.post(
    'http://localhost:8000/execute',
    json={
        'tool': 'repo_analyzer',
        'params': {
            'repo_url': 'https://github.com/THUDM/GLM',
            'analyze_readme': True,
            'analyze_structure': True
        }
    }
)

result = response.json()
print(result['result']['analysis']['readme']['summary'])
```

## 错误处理

- `400`: 请求参数错误
- `500`: 服务器内部错误或API调用失败

## 安全注意事项

- 请妥善保管API密钥
- 限制服务器访问权限
- 考虑添加认证机制
- 验证用户输入以防止注入攻击

## 性能优化

- 结果缓存：对于重复请求，考虑实现缓存机制
- 并发控制：限制并发请求数量以避免API配额耗尽
- 超时设置：合理设置请求超时时间

## 故障排除

1. 如果出现API密钥错误，请检查配置文件中的密钥是否正确
2. 如果服务器无法启动，请检查端口是否被占用
3. 如果API调用失败，请检查网络连接和API配额
4. 如果网页读取失败，请检查目标网站的robots.txt和访问策略

## 扩展性

此服务器设计为可扩展的架构，您可以轻松添加新的工具和功能：

1. 在 `handle_execute` 方法中添加新的工具分支
2. 实现相应的处理函数
3. 在能力描述中添加新工具的元数据

## 许可证

此项目仅供学习和开发使用，请遵守智谱AI的相关使用条款。