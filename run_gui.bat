@echo off
REM Launcher for Civitai Scraper GUI (Windows)

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and run GUI
call venv\Scripts\activate.bat
python civitai_scraper_gui.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred while running the GUI.
    pause
)
