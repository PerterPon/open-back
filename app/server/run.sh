#!/bin/bash

# HTTP服务器启动脚本
# 使用方法: ./run.sh

echo "🚀 启动Python HTTP服务器..."

# 动态设置项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT"

echo "📁 项目根目录：$PROJECT_ROOT"

# 进入服务器目录
cd "$(dirname "$0")"

# 检查依赖是否安装
echo "📦 检查依赖..."
python3 -c "import flask, yaml" 2>/dev/null || {
    echo "⚠️  正在安装依赖..."
    python3 -m pip install -r requirements.txt
}

echo "✅ 依赖检查完成"
echo "🌐 启动服务器 (按 Ctrl+C 停止)..."

# 启动服务器
python3 main.py
