@echo off
setlocal enabledelayedexpansion
title Gym Management App

echo ======================================================
echo              GYM MANAGEMENT APPLICATION              
echo ======================================================
echo.

:: 1. Clean up any leftover processes on ports 8000 and 5173
echo [*] Preparing environment...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 0 } | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

:: 2. Start Backend silently in background (port 8000)
echo [*] Starting Backend server (port 8000)...
powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList '/c cd /d C:\Users\DELL\Desktop\GYM\backend && .\venv\Scripts\activate && uvicorn main:app --port 8000' -WindowStyle Hidden"

:: 3. Start Frontend silently in background (port 5173)
echo [*] Starting Frontend server (port 5173)...
powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList '/c cd /d C:\Users\DELL\Desktop\GYM\frontend && npm run dev' -WindowStyle Hidden"

:: 4. Wait for servers to be ready
echo [*] Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

:: 5. Detect Microsoft Edge or Google Chrome
set "BROWSER="
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
) else if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "BROWSER=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "BROWSER=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

echo [*] Launching Gym App desktop window...
echo.
echo ======================================================
echo  Gym App is active!
echo.
echo  Closing the Gym window will automatically shut down
echo  all servers.
echo ======================================================
echo.

if defined BROWSER (
    set "PROFILE=%TEMP%\gym_app_profile"
    start /wait "" "!BROWSER!" --app=http://localhost:5173 --user-data-dir="!PROFILE!"
) else (
    start "" http://localhost:5173
    echo Press any key when you are finished to stop the servers...
    pause >nul
)

:: 6. Auto-shutdown when the window closes
echo.
echo [*] Gym App window closed. Stopping servers...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 0 } | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

echo [*] All servers stopped successfully. Goodbye!
timeout /t 1 /nobreak >nul
exit
