@echo off
REM ============================================================================
REM MAHER AI - Quick Restart Script
REM ============================================================================
REM This script stops any running instances and restarts the application
REM ============================================================================

echo.
echo ========================================
echo   MAHER AI - Restart Application
echo ========================================
echo.

REM Kill any existing processes
echo Stopping existing servers...
taskkill /FI "WINDOWTITLE eq MAHER AI - Backend Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MAHER AI - Frontend Dev Server*" /F >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start the application
echo Restarting application...
call start.bat
