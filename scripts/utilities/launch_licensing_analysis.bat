@echo off
title Licensing Analysis Processor
color 07

echo.
echo ========================================
echo   LICENSING ANALYSIS PROCESSOR LAUNCHER
echo ========================================
echo.
echo 🚀 Starting Licensing Analysis Processor...
echo.

REM Check if Python is available
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

echo [91mERROR: Python is not installed or not in PATH[0m
echo Please install Python 3.7+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:python_found
echo [92mFound Python: %PYTHON_CMD%[0m
echo.

REM Check if the main script exists
if not exist "main.py" (
    echo [91mERROR: main.py not found[0m
    echo Please ensure you're in the correct directory.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [92mMain script found: main.py[0m
echo.

REM Launch the licensing analysis processor
echo 🚀 Launching Licensing Analysis Processor...
echo.
%PYTHON_CMD% main.py --cache-path "../InvoicesAI/Invoices/Invoices/cache.json"

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo [91mERROR: The licensing analysis processor encountered an error[0m
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

REM If we get here, the script has finished
echo.
echo [92mLicensing analysis processor has finished successfully.[0m
echo.
pause 