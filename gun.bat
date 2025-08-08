@echo off

set ENV_PATH=D:\bcons_app\myenv\Scripts\activate.bat
set GUNICORN_CMD=gunicorn run:mcp -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000

echo Launching MCP in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Backend\mcp" cmd /k "call %ENV_PATH% && %GUNICORN_CMD%"

echo Launching Agent in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Backend\agent" cmd /k "call %ENV_PATH% && gunicorn run:mcp -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8001"

echo Launching Frontend in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Frontend" cmd /k "call %ENV_PATH% && python run.py"
