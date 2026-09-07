@echo off
chcp 65001 >nul
title 🌍 智慧旅游助手

echo ========================================
echo    🌍 智慧旅游助手 - 启动中...
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误：未找到虚拟环境！
    echo 请先运行：python -m venv venv
    echo 然后运行：venv\Scripts\activate
    echo 再运行：pip install -r requirements.txt
    pause
    exit /b
)

REM 激活虚拟环境并运行app
echo ✅ 正在激活虚拟环境...
call venv\Scripts\activate

echo ✅ 正在启动应用...
echo 📱 浏览器将自动打开 http://localhost:8501
echo.
echo 💡 提示：按 Ctrl+C 可以停止应用
echo ========================================
echo.

streamlit run app.py

pause