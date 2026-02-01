# 安全说明

## 配置文件保护

本项目使用 `.gitignore` 来防止敏感配置文件被提交到版本控制系统中：

- `zhipu_comprehensive_config.json` - 包含实际API密钥，被忽略
- `config.template.json` - 配置文件模板，包含示例值，会被提交

## 部署说明

1. 克隆项目后，复制配置文件模板：
   ```bash
   cp config.template.json zhipu_comprehensive_config.json
   ```

2. 编辑 `zhipu_comprehensive_config.json` 文件，替换 `YOUR_ZHIPU_API_KEY_HERE` 为实际的API密钥

3. 启动服务器：
   ```bash
   python3 zhipu_comprehensive_mcp_enhanced.py
   ```

## 安全最佳实践

- 绝不在代码中硬编码API密钥
- 使用环境变量或配置文件管理API密钥
- 定期轮换API密钥
- 不要在日志中记录API密钥
- 使用最小权限原则配置API密钥