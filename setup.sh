#!/bin/bash

# 智谱AI MCP服务器安全设置脚本

echo "智谱AI MCP服务器设置向导"
echo "========================"

# 检查是否已存在配置文件
if [ -f "zhipu_comprehensive_config.json" ]; then
    echo "检测到现有配置文件，跳过初始化步骤。"
else
    echo "创建配置文件..."
    if [ -f "config.template.json" ]; then
        cp config.template.json zhipu_comprehensive_config.json
        echo "已从模板创建配置文件。"
    else
        echo "错误：找不到配置文件模板 config.template.json"
        exit 1
    fi
fi

# 检查是否已有API密钥
current_key=$(grep -o '"api_key": "[^"]*"' zhipu_comprehensive_config.json | cut -d'"' -f4)

if [ "$current_key" = "YOUR_ZHIPU_API_KEY_HERE" ] || [ -z "$current_key" ]; then
    echo ""
    echo "请输入您的智谱AI API密钥："
    read -s API_KEY
    echo ""
    
    if [ -z "$API_KEY" ]; then
        echo "错误：API密钥不能为空"
        exit 1
    fi
    
    echo "正在更新配置文件..."
    sed -i "s/YOUR_ZHIPU_API_KEY_HERE/$API_KEY/g" zhipu_comprehensive_config.json
    
    echo "API密钥已安全保存到配置文件中。"
else
    echo "已在配置文件中检测到API密钥。"
fi

echo ""
echo "安装依赖..."
pip3 install zhipuai aiohttp beautifulsoup4

echo ""
echo "设置完成！"
echo ""
echo "启动服务器："
echo "  python3 zhipu_comprehensive_mcp_enhanced.py"
echo ""
echo "测试连接："
echo "  curl http://localhost:8000/capabilities"
echo ""