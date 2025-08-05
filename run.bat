@echo off

echo Launching MCP in new tab...
wt -w 0 nt -d "D:\project\bcons\Backend\mcp" cmd /k "call D:\project\myenv\Scripts\activate.bat && python run.py"

echo Launching Agent in new tab...
wt -w 0 nt -d "D:\project\bcons\Backend\agent" cmd /k "call D:\project\myenv\Scripts\activate.bat && python run.py"

echo Launching Frontend in new tab...
wt -w 0 nt -d "D:\project\bcons\Frontend" cmd /k "call D:\project\myenv\Scripts\activate.bat && python run.py"