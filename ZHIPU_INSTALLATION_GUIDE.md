# 智谱AI Comprehensive MCP Server - 安装指南

## 系统要求

- Python 3.8 或更高版本
- 稳定的互联网连接
- 至少 512MB 可用内存

## 安装步骤

### 1. 克隆或下载项目文件
确保以下文件都在您的工作目录中：
- `zhipu_comprehensive_mcp.py`
- `zhipu_comprehensive_config.json`
- `start_zhipu_comprehensive.sh`
- `ZHIPU_COMPREHENSIVE_MCP_README.md`
- `test_comprehensive_mcp.py`

### 2. 安装Python依赖
```bash
pip install zhipuai aiohttp beautifulsoup4
```

或者使用requirements.txt（如果存在）：
```bash
pip install -r requirements.txt
```

### 3. 获取智谱AI API密钥
1. 访问 [智谱AI开放平台](https://bigmodel.cn)
2. 注册账号并登录
3. 进入开发者中心
4. 创建新应用或选择现有应用
5. 获取API密钥

### 4. 配置API密钥
编辑 `zhipu_comprehensive_config.json` 文件：
```json
{
  "zhipu": {
    "api_key": "YOUR_ACTUAL_API_KEY_HERE",
    ...
  }
}
```

将 `YOUR_ACTUAL_API_KEY_HERE` 替换为您实际的API密钥。

### 5. 设置执行权限
```bash
chmod +x start_zhipu_comprehensive.sh
chmod +x test_comprehensive_mcp.py
```

### 6. 启动服务器
```bash
./start_zhipu_comprehensive.sh
```

服务器将在 `http://localhost:8000` 上运行。

## 验证安装

### 1. 检查服务器状态
访问 `http://localhost:8000/capabilities` 查看服务器能力信息。

### 2. 运行测试脚本
```bash
./test_comprehensive_mcp.py
```

### 3. 手动测试API
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "text_generator",
    "params": {
      "prompt": "你好，世界！",
      "model": "glm-4"
    }
  }'
```

## 常见问题解决

### 问题1: 模块未找到
**错误**: `ModuleNotFoundError: No module named 'zhipuai'`
**解决**: 运行 `pip install zhipuai`

### 问题2: 端口被占用
**错误**: `OSError: [Errno 98] Address already in use`
**解决**: 杀死占用端口的进程或修改配置文件中的端口号

### 问题3: API密钥无效
**错误**: `AuthenticationError` 或 `401 Unauthorized`
**解决**: 检查配置文件中的API密钥是否正确

### 问题4: 网络连接问题
**错误**: `requests.exceptions.ConnectionError`
**解决**: 检查网络连接和防火墙设置

## 配置选项

### 服务器配置
在 `zhipu_comprehensive_config.json` 中可以调整：

- `server.host`: 服务器主机地址 (默认: localhost)
- `server.port`: 服务器端口 (默认: 8000)
- `zhipu.api_key`: 智谱AI API密钥
- `zhipu.default_model`: 默认使用的模型
- `zhipu.timeout`: API请求超时时间

### 功能开关
在配置文件的 `features` 部分可以启用/禁用特定功能：

```json
"features": {
  "web_search": true,
  "web_reader": true,
  "repo_analyzer": true,
  "vision_analyzer": true,
  "text_generation": true
}
```

## 性能优化

### 1. 连接池配置
对于高并发场景，可以调整连接池大小。

### 2. 缓存机制
实现结果缓存以减少重复API调用。

### 3. 请求限制
实施速率限制以避免超出API配额。

## 安全建议

### 1. API密钥保护
- 不要将API密钥提交到版本控制系统
- 使用环境变量或加密存储
- 定期轮换API密钥

### 2. 访问控制
- 限制服务器访问权限
- 考虑添加身份验证中间件
- 使用HTTPS保护数据传输

### 3. 输入验证
- 验证所有用户输入
- 防止注入攻击
- 限制请求大小

## 监控和日志

### 日志级别
在生产环境中，可以调整日志级别：
- DEBUG: 详细调试信息
- INFO: 基本操作信息
- WARNING: 警告信息
- ERROR: 错误信息

### 性能监控
- 监控API调用频率
- 跟踪错误率
- 监控响应时间

## 更新和维护

### 1. 更新依赖
定期更新Python包以获取最新功能和安全补丁：
```bash
pip list --outdated
pip install --upgrade zhipuai aiohttp beautifulsoup4
```

### 2. 备份配置
定期备份配置文件和重要数据。

### 3. 版本管理
关注智谱AI SDK的版本更新，及时升级以获取新功能。

## 卸载

### 1. 停止服务器
按 `Ctrl+C` 停止运行的服务器。

### 2. 删除文件
删除项目相关文件：
```bash
rm -f zhipu_comprehensive_mcp.py
rm -f zhipu_comprehensive_config.json
rm -f start_zhipu_comprehensive.sh
rm -f ZHIPU_COMPREHENSIVE_MCP_README.md
rm -f test_comprehensive_mcp.py
rm -f ZHIPU_PROJECT_SUMMARY.md
rm -f ZHIPU_INSTALLATION_GUIDE.md
```

### 3. 可选：卸载Python包
如果不再需要这些包：
```bash
pip uninstall zhipuai aiohttp beautifulsoup4
```

## 支持

如果遇到问题，请检查：
1. 是否按照安装步骤正确操作
2. API密钥是否正确配置
3. 网络连接是否正常
4. 依赖包是否正确安装

如需进一步帮助，请参考智谱AI官方文档或联系技术支持。