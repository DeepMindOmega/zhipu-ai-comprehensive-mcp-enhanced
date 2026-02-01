#!/bin/bash

# 智谱AI综合MCP服务器启动脚本

set -e

echo "智谱AI综合MCP服务器启动脚本"
echo "============================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi

# 检查必要依赖
MISSING_DEPS=()

ALL_DEPS=("zhipuai" "aiohttp" "beautifulsoup4" "sniffio" "httpx" "anyio" "typing_extensions")

for dep in "${ALL_DEPS[@]}"; do
    # 将连字符转换为下划线进行Python导入测试
    dep_import=$(echo "$dep" | sed 's/-/_/g')
    if ! python3 -c "import $dep_import" &> /dev/null; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "安装缺失的依赖..."
    pip3 install "${MISSING_DEPS[@]}"
fi

# 额外检查zhipuai的核心依赖
if ! python3 -c "import zhipuai.core._utils._utils" &> /dev/null; then
    echo "安装zhipuai核心依赖..."
    pip3 install sniffio httpx anyio
fi

# 检查配置文件
CONFIG_FILE="/home/admin/zhipu/zhipu_comprehensive_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在 $CONFIG_FILE"
    exit 1
fi

# 检查API密钥是否已设置
API_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['zhipu']['api_key'])")
if [ "$API_KEY" = "YOUR_ZHIPU_API_KEY_HERE" ]; then
    echo "警告: 请先在 $CONFIG_FILE 中设置有效的ZHIPU_API_KEY"
    echo "请访问 https://bigmodel.cn 获取API密钥"
    exit 1
fi

# 设置API密钥环境变量
export ZHIPU_API_KEY="$API_KEY"

echo "配置检查完成"
echo "启动智谱AI综合MCP服务器..."

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    echo "警告: 端口8000已被占用，请停止其他服务或更改端口"
    read -p "是否继续? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "服务器将在 http://localhost:8000 上运行"
echo "按 Ctrl+C 停止服务器"

# 启动服务器
cd /home/admin/zhipu
python3 zhipu_comprehensive_mcp.py