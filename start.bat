@echo off
chcp 65001 >nul
echo ========================================
echo    FootHub 竞彩足球资讯系统 启动脚本
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
)

echo [2/3] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo [3/3] 启动后端服务...
echo.
echo 后端服务地址: http://localhost:5000
echo 前端页面请打开: frontend/index.html
echo.
python app.py
