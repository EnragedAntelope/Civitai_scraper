# Civitai Image Prompt Scraper

A Python tool to scrape image prompts from Civitai based on base model architecture (SD 1.5, SDXL, Pony, Flux, etc.). Available as both a GUI application and command-line tool.

## Features

- **Cross-platform GUI** - Easy-to-use graphical interface for all platforms (Windows, macOS, Linux)
- **Command-line interface** - For automation and scripting
- Scrape images and prompts by base model architecture (Flux, Pony, SDXL, SD 1.5, etc.)
- Optional filtering by model type (Checkpoint, LORA, TextualInversion, etc.)
- Extract detailed metadata including:
  - Positive and negative prompts
  - Generation parameters (seed, steps, sampler, CFG scale)
  - Base model architecture
  - Model information
  - Image dimensions
- Export data to JSON format
- Optional text-only prompt export
- Configurable sorting and pagination
- Rate limiting to avoid API throttling
- Real-time progress tracking

## Quick Start

### Automated Installation (Recommended)

The easiest way to get started is using the automated installer:

**Windows:**
1. Double-click `START_HERE.bat` for an interactive menu, OR
2. Double-click `install.bat` to install
3. Then double-click `run_gui.bat` to launch the GUI

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
./run_gui.sh
```

The installer will:
- Create a virtual environment (venv)
- Install all required dependencies
- Set up launcher scripts

### Manual Installation

If you prefer manual installation:

1. Install Python 3.7 or higher

2. Create virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Application (Recommended)

**Using launcher scripts (after running installer):**

Windows:
```bash
run_gui.bat
```

Linux/macOS:
```bash
./run_gui.sh
```

**Manual launch:**
```bash
# Activate venv first
python civitai_scraper_gui.py
```

The GUI provides:
- Dropdown menus for all base models and options
- Real-time progress monitoring
- Log output showing scraping status
- Easy directory selection
- Start/Stop controls
- All configuration options in one window

**GUI Screenshot:**
The interface includes:
- Base Model selection (Flux, SDXL, Pony, SD 1.5, etc.)
- Optional Model Type filter
- Max Models to scrape
- Sort order selection
- Request delay configuration
- Output directory selection with browse button
- Export prompts checkbox
- Real-time log output
- Progress indicator
- Start/Stop/Clear Log buttons

### Command Line Interface

**Using launcher scripts (after running installer):**

Windows:
```bash
run_cli.bat --base-model "Flux.1 D" --max-models 10
```

Linux/macOS:
```bash
./run_cli.sh --base-model "Flux.1 D" --max-models 10
```

**Manual launch:**
```bash
# Activate venv first
python civitai_scraper.py --base-model "Flux.1 D" --max-models 10
```

### Command Line Arguments

- `--base-model` (required): Base model architecture to scrape
  - Examples: `SD 1.5`, `SDXL 1.0`, `Pony`, `Flux.1 D`, `Flux.1 S`, `SD 1.5 LCM`, `SDXL Turbo`, etc.
  - See the full list of available base models in the Common Base Models section below

- `--model-type` (optional): Filter by model type
  - Choices: `Checkpoint`, `LORA`, `LoCon`, `TextualInversion`, `Hypernetwork`, `AestheticGradient`, `Controlnet`, `Poses`

- `--max-images` (optional): Maximum number of images to scrape
  - Default: 100

- `--sort` (optional): Sort order for images
  - Choices: `Most Reactions`, `Most Comments`, `Newest`
  - Default: `Most Reactions`

- `--output-dir` (optional): Output directory for scraped data
  - Default: `output`

- `--delay` (optional): Delay between API requests in seconds
  - Default: 1.0

- `--export-prompts` (optional): Export prompts to a separate text file

- `--double-spaced` (optional): Use double line spacing in exported prompts file
  - Only applies when `--export-prompts` is used
  - Adds extra blank line between each prompt for better readability

- `--no-strict-filter` (optional): Disable strict base model filtering
  - By default, only images matching the exact base model are included
  - Use this flag to include mixed results when base model has limited images

### Common Base Models

Based on the image you provided, here are the common base model architectures:

**Flux Models:**
- `Flux.1 D`
- `Flux.1 S`

**SDXL Models:**
- `SDXL 1.0`
- `SDXL 1.0 LCM`
- `SDXL Turbo`
- `SDXL Lightning`
- `SDXL Hyper`
- `SDXL Distilled`

**Stable Diffusion Models:**
- `SD 1.5`
- `SD 1.5 LCM`
- `SD 1.5 Hyper`
- `SD 2.1`
- `SD 2.0`

**Pony Models:**
- `Pony`
- `Pony V7`

**Other Models:**
- `AuraFlow`
- `Chroma`
- `CogVideoX`
- `HiDream`
- `Hunyuan 1`
- `Hunyuan Video`
- `Illustrious`
- `Kolors`
- `LTXV`
- `Lumina`
- `Mochi`
- `NoobAI`
- `PixArt a`
- `PixArt E`
- `Qwen`

**Wan Video Models:**
- `Wan Video 1.3B v2v`
- `Wan Video 14B v2v`
- `Wan Video 14B v2v 480p`
- `Wan Video 14B v2v 720p`
- `Wan Video 2.2 T2V-SB`
- `Wan Video 2.2 I2V-A14B`
- `Wan Video 2.2 T2V-A14B`
- `Wan Video 2.5 T2V`
- `Wan Video 2.5 I2V`

**ZimageTurbo:**
- `ZimageTurbo`

### Examples

**Using launcher scripts:**

Scrape Flux.1 D images:
```bash
# Windows
run_cli.bat --base-model "Flux.1 D" --max-images 100

# Linux/macOS
./run_cli.sh --base-model "Flux.1 D" --max-images 100
```

Scrape Pony LORA images with double-spaced prompts:
```bash
# Windows
run_cli.bat --base-model "Pony" --model-type LORA --max-images 50 --export-prompts --double-spaced

# Linux/macOS
./run_cli.sh --base-model "Pony" --model-type LORA --max-images 50 --export-prompts --double-spaced
```

Scrape ZImageTurbo images with prompts:
```bash
# Windows
run_cli.bat --base-model "ZImageTurbo" --max-images 100 --export-prompts --double-spaced

# Linux/macOS
./run_cli.sh --base-model "ZImageTurbo" --max-images 100 --export-prompts --double-spaced
```

Scrape newest SDXL images:
```bash
# Windows
run_cli.bat --base-model "SDXL 1.0" --sort "Newest" --max-images 150

# Linux/macOS
./run_cli.sh --base-model "SDXL 1.0" --sort "Newest" --max-images 150
```

## Output Format

### JSON Output
The script saves data to `output/civitai_prompts_TIMESTAMP.json` with the following structure:

```json
[
  {
    "model_id": 12345,
    "model_name": "Example Model",
    "model_type": "LORA",
    "base_model": "Flux.1 D",
    "version_id": 67890,
    "version_name": "v1.0",
    "image_url": "https://...",
    "width": 1024,
    "height": 1024,
    "prompt": "beautiful landscape, detailed...",
    "negative_prompt": "ugly, blurry...",
    "seed": 123456789,
    "steps": 30,
    "sampler": "DPM++ 2M Karras",
    "cfg_scale": 7.0,
    "model_hash": "abc123",
    "resources": [...]
  }
]
```

### Text Output (with --export-prompts)
A simplified text file containing only the prompts:

**Without --double-spaced:**
```
beautiful landscape, detailed...

ugly, blurry...

score_9, score_8_up, masterpiece...

```

**With --double-spaced:**
```
beautiful landscape, detailed...

ugly, blurry...


score_9, score_8_up, masterpiece...


```

Each entry contains:
- Positive prompt (always included)
- Negative prompt (if available, on next line)
- Blank line(s) between prompts (1 line normal, 2 lines with --double-spaced)

## API Rate Limiting

The script includes a configurable delay between requests (default 1 second) to avoid overwhelming the Civitai API. Adjust the `--delay` parameter if needed.

## Notes

- The scraper uses the official Civitai API (https://civitai.com/api/v1)
- Not all images have associated prompts
- Some metadata fields may be missing depending on the image
- Large scraping operations may take time due to rate limiting

## License

MIT License
