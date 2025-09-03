#!/bin/bash

# 前端开发服务器启动脚本

echo "🚀 启动 OpenBack 前端管理系统..."

# 进入前端目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 当前目录：$(pwd)"

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install
fi

echo "✅ 依赖检查完成"
echo "🌐 启动开发服务器..."
echo "📝 访问地址: http://localhost:3000"
echo ""

# 启动开发服务器
npm start
