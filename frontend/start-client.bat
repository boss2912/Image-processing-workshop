@echo off
REM ============================================================
REM  Image Processing Client - start script (CLIENT machine)
REM  This machine does NOT process images. It only sends them
REM  to the server and displays the result that comes back.
REM
REM  Requires: Python installed (no extra packages needed)
REM ============================================================
cd /d "%~dp0"

echo Starting local web server on port 8000 ...
echo.
echo   1. A browser will open at  http://localhost:8000
echo   2. In the page, set "Backend URL" to the SERVER machine, e.g.
echo        http://172.20.56.133:5000
echo   3. Click Connect, pick an operation, choose an image, click Process.
echo.
echo Press CTRL+C in this window to stop the client.
echo.

start "" http://localhost:8000
python -m http.server 8000
pause
