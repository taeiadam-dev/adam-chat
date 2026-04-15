@echo off
title ADAM Chat Bridge
color 0A
cd /d "%~dp0"

echo.
echo  ============================================
echo    ADAM CHAT BRIDGE  -  Starting...
echo  ============================================
echo.

:: Free port 3000 if something is using it
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 "') do (
    taskkill /F /PID %%a >nul 2>nul
)

:: ── Try Node.js first ─────────────────────────────────────────────────────────
where node >nul 2>nul
if %errorlevel% == 0 (
    echo  Node.js found. Installing packages...
    call npm install --prefer-offline >nul 2>nul
    call npm install >nul 2>nul
    echo  Starting with Node.js...
    echo.
    echo  *** Keep this window open. Browser opening now... ***
    echo.
    ping -n 3 127.0.0.1 >nul
    start "" "http://localhost:3000"
    node server.js
    goto :crashed
)

:: ── Fallback: Try Python ──────────────────────────────────────────────────────
echo  Node.js not found. Trying Python...
echo.

where python >nul 2>nul
if %errorlevel% == 0 (
    echo  Python found. Starting bridge...
    echo.
    echo  *** Keep this window open. Browser opening now... ***
    echo.
    python bridge.py
    goto :crashed
)

where python3 >nul 2>nul
if %errorlevel% == 0 (
    echo  Python3 found. Starting bridge...
    echo.
    python3 bridge.py
    goto :crashed
)

where py >nul 2>nul
if %errorlevel% == 0 (
    echo  Python (py launcher) found. Starting bridge...
    echo.
    py bridge.py
    goto :crashed
)

:: ── Nothing found ────────────────────────────────────────────────────────────
color 0C
echo.
echo  ================================================
echo   ERROR: Neither Node.js nor Python is installed
echo  ================================================
echo.
echo  Please install ONE of these (both are free):
echo.
echo  Option A - Node.js (recommended):
echo    https://nodejs.org  (click "LTS" version)
echo.
echo  Option B - Python:
echo    https://www.python.org/downloads/
echo    (check "Add Python to PATH" during install!)
echo.
echo  After installing, double-click START.bat again.
echo.
pause
exit /b 1

:crashed
color 0C
echo.
echo  !! The server stopped unexpectedly !!
echo.
echo  Take a screenshot of any error above and send it.
echo.
pause
