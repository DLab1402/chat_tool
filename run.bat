@echo off

echo Launching Frontend in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Frontend" cmd /k "call D:\bcons_app\myenv\Scripts\activate.bat && python run.py"
timeout /t 5 /nobreak

echo Launching Agent in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Backend\agent" cmd /k "call D:\bcons_app\myenv\Scripts\activate.bat && python run.py"
timeout /t 5 /nobreak

echo Launching MCP in new tab...
wt -w 0 nt -d "D:\bcons_app\bcons_app\Backend\mcp" cmd /k "call D:\bcons_app\myenv\Scripts\activate.bat && python run.py"