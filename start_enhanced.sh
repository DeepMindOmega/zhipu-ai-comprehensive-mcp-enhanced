#!/bin/bash

# 智谱AI MCP服务器增强版启动脚本

# 检查配置文件
config_file="zhipu_comprehensive_config.json"
if [ ! -f "$config_file" ]; then
    echo "错误: 配置文件不存在，请先运行 ./setup_enhanced.sh"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: python3未安装或不在PATH中"
    exit 1
fi

# 启动服务器
echo "启动智谱AI MCP服务器增强版..."
echo "配置文件: $config_file"
echo "按Ctrl+C停止服务器"
echo ""

python3 zhipu_comprehensive_mcp_enhanced_v2.py "$config_file"