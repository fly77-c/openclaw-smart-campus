@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   OpenClaw Windows Agent (Hardened)
echo ========================================
echo   Port: 5000
echo   File: agent\agent.py
echo ========================================
echo.

python "agent\agent.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Agent exited with error. Check logs above.
    pause
)
