#!/bin/bash
# 账本 APP 预览服务器（开发模式）

echo "启动账本预览服务器..."
echo "访问: http://localhost:8000"
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    python -m http.server 8000
elif command -v npx &> /dev/null; then
    npx http-server -p 8000
else
    echo "请安装 Python 3 或 Node.js"
    echo "Python: https://python.org"
    echo "Node.js: https://nodejs.org"
fi
