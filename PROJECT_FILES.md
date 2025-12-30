# Project Files Overview

## Core Files

### Python Scripts
- **civitai_scraper.py** - Main CLI scraper with API integration
- **civitai_scraper_gui.py** - Cross-platform GUI application

### Configuration
- **requirements.txt** - Python dependencies (just requests)

## Installation & Launcher Scripts

### Windows
- **install.bat** - Automated installer (creates venv, installs dependencies)
- **run_gui.bat** - Launch GUI application
- **run_cli.bat** - Launch CLI application
- **START_HERE.bat** - Interactive menu for all options

### Linux/macOS
- **install.sh** - Automated installer (creates venv, installs dependencies)
- **run_gui.sh** - Launch GUI application
- **run_cli.sh** - Launch CLI application

## Documentation

- **README.md** - Full documentation with all features and options
- **QUICKSTART.md** - Quick reference guide for common tasks
- **PROJECT_FILES.md** - This file - overview of all project files

## Generated Folders (not in repo)

- **venv/** - Virtual environment (created by installer)
- **output/** - Scraped data output directory (created automatically)
  - Contains JSON files with full metadata
  - Contains TXT files with prompts only (if --export-prompts used)

## File Structure

```
Civitai_scraper/
├── civitai_scraper.py         # CLI scraper
├── civitai_scraper_gui.py     # GUI application
├── requirements.txt           # Dependencies
├── .gitignore                # Git ignore rules
│
├── install.bat               # Windows installer
├── install.sh                # Linux/macOS installer
│
├── run_gui.bat               # Windows GUI launcher
├── run_gui.sh                # Linux/macOS GUI launcher
├── run_cli.bat               # Windows CLI launcher
├── run_cli.sh                # Linux/macOS CLI launcher
├── START_HERE.bat            # Windows interactive menu
│
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
├── PROJECT_FILES.md          # This file
│
├── venv/                     # Virtual environment (auto-created)
└── output/                   # Scraped data (auto-created)
    ├── civitai_prompts_*.json
    └── prompts_only_*.txt
```

## Quick Reference

### First Time Setup
**Windows:** Run `install.bat` or `START_HERE.bat`
**Linux/macOS:** Run `./install.sh`

### Launch GUI
**Windows:** Run `run_gui.bat` or use `START_HERE.bat`
**Linux/macOS:** Run `./run_gui.sh`

### Launch CLI
**Windows:** `run_cli.bat --base-model "Flux.1 D" --max-models 10`
**Linux/macOS:** `./run_cli.sh --base-model "Flux.1 D" --max-models 10`

## Technology Stack

- **Python 3.7+** - Programming language
- **tkinter** - GUI framework (built into Python)
- **requests** - HTTP library for API calls
- **Virtual Environment** - Isolated Python environment

## API Used

- **Civitai API v1** - https://civitai.com/api/v1
  - `/models` - List models with filtering
  - `/models/{id}` - Get model details and images

## Features Summary

- Scrape by base model architecture (Flux, SDXL, Pony, SD 1.5, etc.)
- Optional model type filtering (Checkpoint, LORA, etc.)
- Extract prompts and generation metadata
- JSON and TXT export formats
- Cross-platform GUI and CLI
- Rate limiting and error handling
- Real-time progress tracking
- Automated installation and launchers
