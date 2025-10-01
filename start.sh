#!/bin/bash

# 设置颜色和编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 设置终端标题
echo -e "\033]0;星露谷种子搜索器启动器\007"

echo
echo "╔════════════════════════════════════════╗"
echo "║  🌾 星露谷种子搜索器 - 正在启动...   ║"
echo "╚════════════════════════════════════════╝"
echo

# 检查是否存在必要文件
if [ ! -f "stardew-seed-searcher" ]; then
    echo "[错误] 找不到 stardew-seed-searcher"
    echo "请确保所有文件都在同一目录下！"
    read -p "按任意键继续..."
    exit 1
fi

if [ ! -f "index.html" ]; then
    echo "[错误] 找不到 index.html"
    echo "请确保所有文件都在同一目录下！"
    read -p "按任意键继续..."
    exit 1
fi

# 检查可执行权限
if [ ! -x "stardew-seed-searcher" ]; then
    echo "[提示] 设置可执行权限..."
    chmod +x stardew-seed-searcher
fi

# 启动后端服务
echo "[1/2] 启动后端服务..."
nohup ./stardew-seed-searcher >/dev/null 2>&1 &
SERVER_PID=$!

# 等待服务启动
echo "[2/2] 等待服务启动 (2秒)..."
sleep 2

# 检查服务是否启动成功
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "[错误] 服务启动失败，请检查日志文件 stardew-seed-searcher.log"
    read -p "按任意键继续..."
    exit 1
fi

# 打开网页界面
echo "[完成] 正在打开界面..."

# 检测操作系统并使用相应的命令打开浏览器
if command -v xdg-open >/dev/null 2>&1; then
    # Linux (大多数发行版)
    xdg-open index.html
elif command -v open >/dev/null 2>&1; then
    # macOS
    open index.html
elif command -v firefox >/dev/null 2>&1; then
    # 备用：直接启动Firefox
    firefox index.html &
elif command -v google-chrome >/dev/null 2>&1; then
    # 备用：直接启动Chrome
    google-chrome index.html &
elif command -v chromium-browser >/dev/null 2>&1; then
    # 备用：直接启动Chromium
    chromium-browser index.html &
else
    echo "[提示] 无法自动打开浏览器，请手动打开 index.html"
fi

echo
echo "✓ 启动完成！"
echo
echo "提示："
echo "  - 浏览器会自动打开搜索界面"
echo "  - 关闭终端不会停止服务"
echo "  - 要完全停止，请运行: kill $SERVER_PID"
echo "  - 或查看日志: tail -f stardew-seed-searcher.log"
echo
echo "服务进程ID: $SERVER_PID"
echo "日志文件: stardew-seed-searcher.log (程序自动创建)"
echo

# 保存PID到文件，方便后续停止服务
echo $SERVER_PID > stardew-seed-searcher.pid

read -p "按任意键继续..."
