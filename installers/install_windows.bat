@echo off
REM Windows One-Click Installer for Jarvis AI

echo ========================================
echo    JARVIS AI - Windows Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Python detected
python --version

REM Install dependencies
echo.
echo [2/5] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [3/5] Dependencies installed successfully

REM Check for .env file
if not exist .env (
    echo.
    echo [4/5] Creating .env file from template...
    copy .env.example .env
    echo [IMPORTANT] Please edit .env and add your API key
) else (
    echo [4/5] .env file already exists
)

REM Create data directory if needed
if not exist data mkdir data

REM Create empty memory file if needed
if not exist data\memory.json (
    echo {} > data\memory.json
    echo [5/5] Created memory file
) else (
    echo [5/5] Memory file exists
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API key
echo 2. Run: python installers\doctor.py (to verify)
echo 3. Run: python main.py (to start Jarvis)
echo.
pause
