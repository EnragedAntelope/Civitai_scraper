@echo off
REM Civitai Scraper Installer for Windows
REM This script creates a virtual environment and installs dependencies

echo ========================================
echo Civitai Image Prompt Scraper Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Checking Python version...
python --version

REM Check if venv already exists
if exist "venv" (
    echo.
    echo Virtual environment already exists.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo Keeping existing virtual environment.
        goto :install_deps
    )
)

echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:install_deps
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the scraper:
echo   - GUI version: Double-click run_gui.bat
echo   - CLI version: Double-click run_cli.bat or use run_cli.bat --help
echo.
echo Or manually activate the virtual environment:
echo   venv\Scripts\activate.bat
echo.
pause
