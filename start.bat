@echo off
chcp 65001 >nul
title 星露谷种子搜索器启动器

echo.
echo ╔════════════════════════════════════════╗
echo ║  🌾 星露谷种子搜索器 - 正在启动...   ║
echo ╚════════════════════════════════════════╝
echo.

:: 检查是否存在必要文件
if not exist "stardew-seed-searcher.exe" (
    echo [错误] 找不到 stardew-seed-searcher.exe
    echo 请先运行: go build -o stardew-seed-searcher.exe ./cmd
    pause
    exit /b 1
)

if not exist "index.html" (
    echo [错误] 找不到 index.html
    echo 请确保所有文件都在同一目录下！
    pause
    exit /b 1
)

:: 启动后端服务（隐藏窗口）
echo [1/2] 启动后端服务...
start /min "" stardew-seed-searcher.exe

:: 等待服务启动
echo [2/2] 等待服务启动 (2秒)...
timeout /t 2 /nobreak >nul

:: 打开网页界面
echo [完成] 正在打开界面...
start "" index.html

echo.
echo ✓ 启动完成！
echo.
echo 提示：
echo   - 浏览器会自动打开搜索界面
echo   - 关闭浏览器不会停止服务
echo   - 要完全停止，请关闭所有相关窗口
echo.
pause