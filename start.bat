@echo off
chcp 65001 >nul
title ⚙️ OpenClaw 核心执行器
echo ================================================
echo   ⚙️  OpenClaw 核心执行器 Core Executor v2.0
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python 依赖...
python -c "import flask, requests" 2>nul
if %errorlevel% neq 0 (
    echo    ⚠️ 缺少依赖，正在安装 flask requests...
    pip install flask requests -q
)
python -c "import PIL" 2>nul
if %errorlevel% neq 0 (
    echo    ⚠️ 缺少 Pillow（截屏功能），正在安装...
    pip install pillow -q
)

echo [2/3] 检查 OpenClaw SSH 隧道（可选，AI 桥需要）...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:18789' -TimeoutSec 2 -UseBasicParsing; Write-Host '   ✅ OpenClaw 隧道已连通 (127.0.0.1:18789)' } catch { Write-Host '   ⚠️ 未检测到 OpenClaw 隧道（AI 桥不可用，执行器功能不受影响）' }"

echo [3/3] 启动核心执行器...
echo    按 Ctrl+C 停止服务
echo.
python main.py

pause
