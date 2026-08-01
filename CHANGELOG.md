# Changelog

## Version 2.2 - Live base model / model type list (2026-08-01)

### Improvement

**Base Model / Type dropdowns and filters no longer go stale:**
- Civitai publishes a public, undocumented-until-recently `GET /api/v1/enums`
  endpoint returning the current `BaseModel`, `ModelType`, `ModelFileType`,
  and `BaseModelType` enum values it accepts.
- Added `CivitaiScraper.fetch_enums()` to call it.
- The GUI now fetches this in the background on startup and refreshes the
  Base Model / Type comboboxes with the live list (e.g. picks up newer
  base models like `Krea 2`, `Qwen`, `Wan Video 2.5`, etc. automatically).
  Falls back silently to the bundled static list if the request fails
  (offline, timeout, API change) - never blocks the GUI or shows an error.
- Added `--list-base-models` / `--list-model-types` CLI flags so CLI users
  can check current valid values without opening the docs.
- Updated the bundled fallback lists (used before the live fetch completes,
  or if it fails) to the full current API values as of 2026-07-31, and
  added the missing `Most Collected` / `Oldest` / `Random` sort options
  that Civitai's `/images` endpoint has supported for a while but weren't
  in the GUI's Sort dropdown.

### Known issue (not fixed in this release)

- `--model-type` / the GUI's "Type" filter does not actually filter
  results. Civitai's `/api/v1/images` endpoint has no server-side
  model-type filter parameter (confirmed against the live API - passing
  `types=`/`modelType=` has no effect on results), and the scraper's own
  `get_images_by_filter()` never sends the value it's given either way.
  This predates this release. Implementing real filtering would require
  resolving each image's `modelVersionIds` to a model type via extra
  `/model-versions/{id}` calls (with caching), which is a bigger change
  left for a future PR.

## Version 2.1 - Fixed ZImageTurbo (2025-12-28)

### Critical Fix

**Fixed ZImageTurbo and all base model filtering:**
- Changed API parameter from `baseModel` to `baseModels` (plural)
- This was causing the API to ignore the filter and return mixed results
- Now correctly returns 100% matching images for ANY base model

### Test Results
- ✅ ZImageTurbo: 200/200 images (100% match)
- ✅ All base models now work correctly
- ✅ Strict filtering working as expected

## Version 2.0 - Fixed Image Scraping (2025-12-28)

### Major Changes

**Fixed the "no images scraped" issue:**
- Switched from `/models/{id}` endpoint to `/images` endpoint
- The images endpoint includes full metadata with prompts
- Now successfully scrapes images with prompts and generation parameters

### API Changes

**Endpoint Migration:**
- Old: Used `/api/v1/models` → `/api/v1/models/{id}` (no metadata)
- New: Uses `/api/v1/images` directly (includes all metadata)

**Parameter Changes:**
- `--max-models` → `--max-images` (default: 100)
- Sort options changed to: "Most Reactions", "Most Comments", "Newest"
- Timeout increased from 30s to 60s for better reliability

### Data Structure Changes

**New fields captured:**
- `image_id` - Unique image identifier
- `image_url` - Direct URL to image
- `base_model` - Base model architecture
- `created_at` - Image creation timestamp
- `username` - Creator username
- `post_id` - Associated post ID
- `model_version_ids` - List of model version IDs used

**Metadata fields:**
- `prompt` - Positive prompt
- `negative_prompt` - Negative prompt
- `seed`, `steps`, `sampler`, `cfg_scale`
- `size`, `model_hash`, `hashes`, `resources`

### Bug Fixes

- Fixed NoneType error when metadata is missing
- Added proper null/None handling for all fields
- Improved error handling for API timeouts

### Improvements

- Better progress reporting (shows image count instead of model count)
- More detailed logging in both CLI and GUI
- Export prompts now includes base model and username
- GUI shows real-time image count progress

## Version 1.0 - Initial Release

- Command-line scraper
- Cross-platform GUI
- Automated installation scripts
- Virtual environment support
- Base model filtering
- Model type filtering

