@echo off
REM Civitai Scraper - Quick Launcher
title Civitai Image Prompt Scraper

:menu
cls
echo ========================================
echo   Civitai Image Prompt Scraper
echo ========================================
echo.
echo What would you like to do?
echo.
echo 1. Install / Setup (First time only)
echo 2. Run GUI Application
echo 3. Run CLI (will prompt for options)
echo 4. Open output folder
echo 5. View Quick Start Guide
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto run_gui
if "%choice%"=="3" goto run_cli
if "%choice%"=="4" goto open_output
if "%choice%"=="5" goto view_guide
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:install
cls
echo Running installer...
echo.
call install.bat
pause
goto menu

:run_gui
cls
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Not installed yet!
    echo Please run option 1 to install first.
    echo.
    pause
    goto menu
)
echo Launching GUI...
start "" run_gui.bat
goto end

:run_cli
cls
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Not installed yet!
    echo Please run option 1 to install first.
    echo.
    pause
    goto menu
)
echo.
echo Enter the base model (e.g., "Flux.1 D", "Pony", "SDXL 1.0"):
set /p base_model="Base Model: "
if "%base_model%"=="" (
    echo No base model entered!
    pause
    goto menu
)
echo.
set /p max_models="Max models to scrape (default 10): "
if "%max_models%"=="" set max_models=10
echo.
echo Running scraper...
call run_cli.bat --base-model "%base_model%" --max-models %max_models%
pause
goto menu

:open_output
if exist "output" (
    explorer output
) else (
    echo Output folder doesn't exist yet.
    echo Run the scraper first to create it.
    pause
)
goto menu

:view_guide
if exist "QUICKSTART.md" (
    notepad QUICKSTART.md
) else (
    echo Quick start guide not found.
    pause
)
goto menu

:end
exit
