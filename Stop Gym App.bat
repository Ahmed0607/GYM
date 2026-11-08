@echo off
title Stop Gym Application
echo ======================================================
echo           STOPPING GYM MANAGEMENT SERVERS            
echo ======================================================
echo.
echo [*] Stopping processes on ports 8000 and 5173...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 0 } | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo [*] Done! All backend and frontend servers stopped.
timeout /t 2 /nobreak >nul
exit
