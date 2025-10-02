@echo off
title Stardew Seed Searcher

echo.
echo ================================================
echo   Stardew Seed Searcher - Starting...
echo ================================================
echo.

if not exist "stardew-seed-searcher.exe" (
    echo [ERROR] stardew-seed-searcher.exe not found
    echo Please run: go build -o stardew-seed-searcher.exe .
    pause
    exit /b 1
)

if not exist "index.html" (
    echo [ERROR] index.html not found
    echo Please make sure all files are in the same directory!
    pause
    exit /b 1
)

echo [1/2] Starting backend service...
start /min "" stardew-seed-searcher.exe

echo [2/2] Waiting for service to start (2 seconds)...
timeout /t 2 /nobreak >nul

echo [DONE] Opening interface...
start "" index.html

echo.
echo Startup complete!
echo.
echo Tips:
echo   - Browser will open the search interface
echo   - Closing browser will not stop the service
echo   - To stop completely, close all related windows
echo.
pause