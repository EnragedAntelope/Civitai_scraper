# AGENTS.md — Civitai_scraper

Scrape image prompts and metadata from Civitai. Filter by base model, sort order, time period, and more. Includes a Prompt Miner that finds high-quality prompts for specific subjects using weighted keyword scoring. Cross-platform GUI and CLI. Python 3.7+, requests-only dependency.

## Architecture in 60 seconds

- **Two main features:** Image Scraper (bulk-scrape images & prompts with filters) and Prompt Miner (find best prompts for a subject with smart scoring).
- **Dual interface:** GUI (`civitai_scraper_gui.py`) and CLI (`civitai_scraper.py`). Both share the same output options.
- **Image Scraper:** Filter by base model, model type, sort order, time period, NSFW level, username. Set max images and request delay.
- **Prompt Miner:** Built-in presets (Space, Fantasy, Cyberpunk, Nature, Architecture, Horror, etc.) or custom presets. Configure search keywords with weights, required/banned words, quality filters (min length, max commas, min score), target count.
- **Custom presets** stored in `custom_presets.json` (git-ignored, survives pulls).
- **Flexible output:** JSON metadata + cleaned text prompts, with formatting options (one-per-line, separators, positive-only).
- **Preset-prefixed filenames:** Mining output files automatically prefixed with preset name.

## Layout

| File | Purpose |
|------|---------|
| `civitai_scraper.py` | CLI for image scraping and prompt mining |
| `civitai_scraper_gui.py` | GUI (two tabs: Image Scraper + Prompt Miner) |
| `install.bat` / `install.sh` | One-time setup (venv + requirements) |
| `run_gui.bat` / `run_gui.sh` | Launch the GUI |
| `run_cli.bat` / `run_cli.sh` | Launch the CLI |
| `START_HERE.bat` | Windows quick start |
| `requirements.txt` | requests only |

## Build / test / run

```bash
# Windows quick start
START_HERE.bat

# Or manual setup
install.bat        # Windows
./install.sh       # Linux/macOS

# Launch GUI
run_gui.bat        # Windows
./run_gui.sh       # Linux/macOS

# Launch CLI
run_cli.bat        # Windows
./run_cli.sh       # Linux/macOS

# Manual setup
python -m venv venv && venv\Scripts\activate   # Windows
python3 -m venv venv && source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# CLI usage examples
python civitai_scraper.py --base-model "Flux.1 D" --max-images 100 --export-prompts
python civitai_scraper.py --base-model "Pony" --model-type LORA --sort "Newest" --period Month
python civitai_scraper.py --mine --preset "Space / Sci-Fi" --target-count 50
```

## Conventions & gotchas

- Single dependency: requests. No torch, no heavy libraries.
- Custom presets are git-ignored (`custom_presets.json`) — they persist between sessions and survive git pulls.
- Built-in presets cover 13 themes: Space, Fantasy, Cyberpunk, Nature, Architecture, Futuristic, Horror, Gigantism, Micro-World, Retro-Futuristic, Underwater, Steampunk, Post-Apocalyptic.
- Output directory defaults to `output/` (also git-ignored).
- API rate limiting: set request delay in GUI/CLI to avoid Civitai rate limits.
- NSFW filtering: None/Low/Medium/High/Blocked levels available.

## Security

This file is **public-safe by default**. Never add local paths, credentials, API keys, personal data, infrastructure details, or subscription info.

Before pushing: `pwsh scripts/check-agents-md.ps1 AGENTS.md CLAUDE.md` — must exit 0.

**Civitai API key** is entered in the GUI or via CLI flag. Never commit it.

## Maintenance

**Update rule:** When you change the architecture, build/test commands, or conventions, update this AGENTS.md in the same commit. Keep under 200 lines.

**CLAUDE.md:** One-line shim: `@AGENTS.md`.

**New-repo rule:** Create AGENTS.md in the first session a new repo is worked on.

**No-overlap rule:** Explanatory prose lives in one file. AGENTS.md = agent-facing summary; README.md = human/usage. Identical commands may be restated verbatim. Explanatory prose must not be duplicated — link instead.
