# Civitai Image Prompt Scraper

Scrape image prompts and metadata from Civitai. Filter by base model, sort order, time period, and more. Includes a **Prompt Miner** that finds high-quality prompts for specific subjects using weighted keyword scoring.

Available as a cross-platform **GUI** and **CLI**.

## Key Features

- **Image Scraper** - Bulk-scrape images & prompts filtered by base model, model type, user, NSFW level, etc.
- **Prompt Miner** - Find the best prompts for a subject (space, fantasy, horror, etc.) with smart scoring and filtering
- **Custom Presets** - Save your own mining presets; they persist between sessions and survive git pulls
- **Flexible Output** - JSON metadata + cleaned text prompts, with formatting options (one-per-line, separators, positive-only)
- **Preset-prefixed Filenames** - Mining output files are automatically prefixed with the preset name

## Quick Start

### Windows
```
START_HERE.bat
```
Or: `install.bat` then `run_gui.bat`

### Linux / macOS
```bash
chmod +x install.sh && ./install.sh
./run_gui.sh
```

### Manual
```bash
python -m venv venv && venv\Scripts\activate   # Windows
python3 -m venv venv && source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python civitai_scraper_gui.py
```

## GUI

The GUI has two tabs sharing a common **Output** section:

### Image Scraper Tab
Filter by base model, model type, sort order, time period, NSFW level, and username. Set max images and request delay.

### Prompt Miner Tab
Select a built-in preset or create your own. Configure search keywords (with optional weights), required/banned words, quality filters (min length, max commas, min score), and target count.

**Custom Presets:** Click **Save...** to save current mining settings as a named preset. Click **Delete** to remove a custom preset. Custom presets are stored in `custom_presets.json` (git-ignored, survives pulls).

### Shared Output Section
Both tabs share output settings: directory, JSON/text format toggles, API key, and text formatting options (one-per-line, positive-only, separators, double-spaced).

## Built-in Mining Presets

| Preset | Focus |
|--------|-------|
| Space / Sci-Fi | Spaceships, nebulae, planets, zero-gravity |
| Fantasy / Medieval | Castles, dragons, knights, magic |
| Cyberpunk | Neon, holograms, dystopian megacities |
| Nature / Landscape | Mountains, oceans, auroras, wilderness |
| Architecture / Urban | Skylines, cathedrals, brutalist structures |
| Futuristic | High-tech, mecha, sleek metropolises |
| Horror | Macabre, haunted, lovecraftian, gothic |
| Gigantism | Colossal structures, scale comparisons |
| Micro-World | Miniatures, dioramas, tilt-shift |
| Retro-Futuristic | Atompunk, googie, cassette-futurism |
| Underwater | Deep sea, bioluminescent, coral reefs |
| Steampunk | Clockwork, brass, victorian airships |
| Post-Apocalyptic | Wastelands, ruins, overgrown decay |

## CLI Usage

### Image Scraping
```bash
python civitai_scraper.py --base-model "Flux.1 D" --max-images 100 --export-prompts
python civitai_scraper.py --base-model "Pony" --model-type LORA --sort "Newest" --period Month
python civitai_scraper.py --username "someuser" --max-images 50 --nsfw None
```

### Prompt Mining
```bash
python civitai_scraper.py --mine --mine-preset "Space / Sci-Fi" --mine-target 50
python civitai_scraper.py --mine --mine-keywords "dragon:3,castle:2,magic" --mine-min-score 3
```

### CLI Arguments

**Scraping:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--base-model` | *all* | Base model filter (e.g. `Flux.1 D`, `SDXL 1.0`, `Pony`) |
| `--model-type` | *all* | Checkpoint, LORA, LoCon, TextualInversion, etc. |
| `--max-images` | 100 | Max images to scrape |
| `--sort` | Most Reactions | Most Reactions, Most Comments, Newest |
| `--period` | AllTime | AllTime, Year, Month, Week, Day |
| `--nsfw` | *any* | None, Soft, Mature, X |
| `--username` | - | Filter by Civitai username |
| `--output-dir` | output | Output directory |
| `--delay` | 1.0 | Seconds between API requests |
| `--export-prompts` | off | Also save a text file of prompts |
| `--double-spaced` | off | Extra spacing in text output |
| `--use-separator` | off | Separator lines between prompts |
| `--no-strict-filter` | off | Allow mixed base model results |
| `--api-key` | - | Civitai API key for authenticated access |

**Mining:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--mine` | - | Enable mining mode |
| `--mine-preset` | - | Use a built-in preset name |
| `--mine-keywords` | - | `word:weight` pairs (e.g. `cockpit:2,thruster:3`) |
| `--mine-required` | - | At least one must appear |
| `--mine-banned` | - | Instant rejection words |
| `--mine-min-length` | 100 | Min prompt character length |
| `--mine-max-commas` | 15 | Max commas (filters tag-soup) |
| `--mine-min-score` | 3 | Min keyword match score |
| `--mine-target` | 50 | Stop after N matches |

## Output

**JSON** (`civitai_prompts_TIMESTAMP.json`): Full metadata including prompt, negative prompt, seed, steps, sampler, CFG scale, base model, image URL, dimensions, and resources.

**Text** (`prompts_only_TIMESTAMP.txt`): Prompts in plain text. Options: one-per-line (cleaned), positive-only, separators, double-spaced.

**Mining output** is prefixed with the preset name: `Space_Sci-Fi_mined_prompts_TIMESTAMP.json`

## Notes

- Uses the official [Civitai API v1](https://civitai.com/api/v1)
- Not all images have prompts; the scraper reports counts
- Rate limiting is configurable via the delay setting
- Custom presets are saved to `custom_presets.json` (automatically git-ignored)

## License

MIT License
