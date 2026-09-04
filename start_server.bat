@echo off
cd /d "%~dp0"
start "Mapper3000 Server" cmd /k python server.py
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/garage-sale-map.html"
