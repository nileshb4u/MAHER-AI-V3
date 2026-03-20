@echo off
REM ============================================================================
REM MAHER AI - Stop Application Script
REM ============================================================================
REM This script stops all running MAHER AI servers
REM ============================================================================

echo.
echo ========================================
echo   MAHER AI - Stopping Application
echo ========================================
echo.

echo Stopping backend server...
taskkill /FI "WINDOWTITLE eq MAHER AI - Backend Server*" /F >nul 2>&1
if errorlevel 1 (
    echo Backend server was not running.
) else (
    echo Backend server stopped.
)

echo.
echo Stopping frontend dev server...
taskkill /FI "WINDOWTITLE eq MAHER AI - Frontend Dev Server*" /F >nul 2>&1
if errorlevel 1 (
    echo Frontend dev server was not running.
) else (
    echo Frontend dev server stopped.
)

echo.
echo ========================================
echo   All servers stopped!
echo ========================================
echo.
pause
