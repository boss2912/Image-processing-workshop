@echo off
REM ============================================================
REM  Image Processing Backend - start script (SERVER machine)
REM  Run this on the machine that will do the image processing.
REM ============================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    echo [2/3] Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
) else (
    echo [1/3] Virtual environment found - skipping setup.
    echo [2/3] Skipping install.
)

echo.
echo [3/3] This machine's IPv4 addresses:
ipconfig | findstr /i "IPv4"
echo.
echo Give the CLIENT machine one of the addresses above with port 5000
echo   example:  http://172.20.56.133:5000
echo.
echo Starting server on 0.0.0.0:5000 ... press CTRL+C to stop
echo.

set FLASK_DEBUG=0
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
".venv\Scripts\python.exe" app.py
pause
