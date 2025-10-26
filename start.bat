@echo off
REM Aesop AI - Quick Start Script for Windows

echo ==================================
echo Starting Aesop AI
echo ==================================

REM Check if running from correct directory
if not exist "backend" goto :error
if not exist "frontend" goto :error

REM Start backend server
echo.
echo Starting backend server on http://localhost:8000
cd backend
start "Aesop AI Backend" cmd /k python main.py
timeout /t 3 /nobreak >nul

REM Start frontend server
echo.
echo Starting frontend server on http://localhost:8080
cd ..\frontend
start "Aesop AI Frontend" cmd /k python -m http.server 8080

echo.
echo ==================================
echo Aesop AI is running!
echo ==================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080/record.html
echo.
echo Close the server windows to stop
echo ==================================

goto :end

:error
echo Error: Please run this script from the project root directory
pause
exit /b 1

:end

