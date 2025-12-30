# Quick Start Guide

## First Time Setup

### Windows
1. Double-click `install.bat`
2. Wait for installation to complete
3. You're ready to go!

### Linux/macOS
```bash
chmod +x install.sh
./install.sh
```

## Running the Scraper

### GUI Mode (Easiest)

**Windows:** Double-click `run_gui.bat`

**Linux/macOS:**
```bash
./run_gui.sh
```

The GUI has all options in one window:
1. Select base model (e.g., "Flux.1 D", "Pony", "SDXL 1.0")
2. Set max models to scrape
3. Click "Start Scraping"
4. Watch the log for progress

### Command Line Mode

**Windows:**
```bash
run_cli.bat --base-model "Flux.1 D" --max-models 10
```

**Linux/macOS:**
```bash
./run_cli.sh --base-model "Flux.1 D" --max-models 10
```

### Common Commands

Scrape 20 Flux models:
```bash
# Windows
run_cli.bat --base-model "Flux.1 D" --max-models 20

# Linux/macOS
./run_cli.sh --base-model "Flux.1 D" --max-models 20
```

Scrape Pony LORA models and export prompts:
```bash
# Windows
run_cli.bat --base-model "Pony" --model-type LORA --export-prompts

# Linux/macOS
./run_cli.sh --base-model "Pony" --model-type LORA --export-prompts
```

Get help:
```bash
# Windows
run_cli.bat --help

# Linux/macOS
./run_cli.sh --help
```

## Where Are My Results?

Results are saved in the `output/` directory:
- `civitai_prompts_TIMESTAMP.json` - Full data with all metadata
- `prompts_only_TIMESTAMP.txt` - Just the prompts (if --export-prompts used)

## Troubleshooting

**Virtual environment not found:**
- Run the installer first: `install.bat` (Windows) or `./install.sh` (Linux/macOS)

**Python not found:**
- Install Python 3.7+ from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

**Permission denied (Linux/macOS):**
```bash
chmod +x *.sh
```

## Popular Base Models

- `Flux.1 D` - Flux diffusion model
- `Flux.1 S` - Flux schnell model
- `SDXL 1.0` - Stable Diffusion XL
- `SDXL Lightning` - Fast SDXL variant
- `Pony` - Pony diffusion model
- `SD 1.5` - Stable Diffusion 1.5
- `SD 2.1` - Stable Diffusion 2.1

See README.md for the complete list of base models.

## Need More Help?

See the full README.md for detailed documentation and all available options.
