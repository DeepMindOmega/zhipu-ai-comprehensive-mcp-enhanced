#!/bin/bash

# 智谱AI MCP服务器增强版安全设置脚本

echo "智谱AI MCP服务器增强版设置向导"
echo "================================="

# 检查Python版本
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.7或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✓ Python版本检查通过: $python_version"

# 检查是否已存在配置文件
config_file="zhipu_comprehensive_config.json"
enhanced_config_file="config_enhanced.json"

if [ -f "$config_file" ]; then
    echo "检测到现有配置文件，将创建增强版配置文件..."
    if [ -f "$enhanced_config_file" ]; then
        echo "检测到增强版配置文件已存在，跳过初始化步骤。"
    else
        cp config_enhanced.json "$config_file"
        echo "✓ 已创建增强版配置文件。"
    fi
else
    if [ -f "$enhanced_config_file" ]; then
        cp "$enhanced_config_file" "$config_file"
        echo "✓ 已从增强版模板创建配置文件。"
    elif [ -f "config.template.json" ]; then
        cp config.template.json "$config_file"
        echo "✓ 已从基础模板创建配置文件。"
    else
        echo "错误：找不到配置文件模板"
        exit 1
    fi
fi

# 检查是否已有API密钥
current_key=$(grep -o '"api_key": "[^"]*"' "$config_file" | cut -d'"' -f4)

if [ "$current_key" = "输入你的智谱api insert your api here" ] || [ "$current_key" = "YOUR_ZHIPU_API_KEY_HERE" ] || [ -z "$current_key" ]; then
    echo ""
    echo "请输入您的智谱AI API密钥（可选，输入skip跳过）："
    read -s API_KEY
    echo ""
    
    if [ -z "$API_KEY" ]; then
        echo "警告: 未设置API密钥，部分功能将不可用"
    elif [ "$API_KEY" = "skip" ]; then
        echo "跳过API密钥设置，稍后可手动配置"
    else
        echo "正在更新配置文件..."
        sed -i "s/输入你的智谱api insert your api here/$API_KEY/g" "$config_file"
        echo "✓ API密钥已安全保存到配置文件中"
    fi
else
    echo "✓ 已在配置文件中检测到API密钥"
fi

# 安装依赖
echo ""
echo "安装Python依赖..."

# 创建requirements.txt如果不存在
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
aiohttp>=3.8.0
beautifulsoup4>=4.11.0
zhipuai>=2.0.0
EOF
    echo "✓ 已创建requirements.txt文件"
fi

# 安装依赖
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✓ 依赖安装成功"
    else
        echo "⚠ 依赖安装可能存在问题，请检查错误信息"
    fi
else
    echo "错误: pip3未安装或不在PATH中"
    exit 1
fi

# 验证配置文件
echo ""
echo "验证配置文件..."
if python3 config_validator.py "$config_file"; then
    echo "✓ 配置文件验证通过"
else
    echo "⚠ 配置文件验证失败，请检查配置"
fi

# 创建缓存目录
cache_dir="cache"
if [ ! -d "$cache_dir" ]; then
    mkdir -p "$cache_dir"
    echo "✓ 已创建缓存目录: $cache_dir"
fi

# 创建日志目录
log_dir="logs"
if [ ! -d "$log_dir" ]; then
    mkdir -p "$log_dir"
    echo "✓ 已创建日志目录: $log_dir"
fi

# 设置启动脚本权限
chmod +x start_zhipu_comprehensive.sh start_zhipu_vision.sh
echo "✓ 已设置启动脚本权限"

# 创建增强版启动脚本
cat > start_enhanced.sh << 'EOF'
#!/bin/bash

# 智谱AI MCP服务器增强版启动脚本

# 检查配置文件
config_file="zhipu_comprehensive_config.json"
if [ ! -f "$config_file" ]; then
    echo "错误: 配置文件不存在，请先运行 ./setup.sh"
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
EOF

chmod +x start_enhanced.sh
echo "✓ 已创建增强版启动脚本: start_enhanced.sh"

echo ""
echo "设置完成！"
echo ""
echo "启动服务器选项："
echo "1. 基础服务器:"
echo "   python3 zhipu_comprehensive_mcp_enhanced.py"
echo ""
echo "2. 增强版服务器（推荐）:"
echo "   ./start_enhanced.sh"
echo "   或:"
echo "   python3 zhipu_comprehensive_mcp_enhanced_v2.py"
echo ""
echo "3. 测试连接："
echo "   curl http://localhost:8000/capabilities"
echo ""
echo "4. 健康检查："
echo "   curl http://localhost:8000/health"
echo ""
echo "5. 缓存统计："
echo "   curl http://localhost:8000/cache/stats"
echo ""

echo "新功能特性："
echo "- ✅ 配置文件验证"
echo "- ✅ 增强错误处理"
echo "- ✅ 请求缓存机制"
echo "- ✅ 请求频率限制"
echo "- ✅ API密钥认证（可选）"
echo "- ✅ CORS支持"
echo "- ✅ 详细日志记录"
echo "- ✅ 健康检查端点"
echo "- ✅ 缓存管理端点"
echo ""