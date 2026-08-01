# Changelog

## Version 2.2 - Fixed missing prompts/meta (2026-07-31)

### Critical Fix

**Fixed scraper returning no prompts or generation metadata:**
- Civitai's `/api/v1/images` endpoint now omits the `meta` object (prompt,
  negative prompt, seed, steps, sampler, resources, etc.) unless the request
  explicitly includes `withMeta=true`. Previously the API included `meta` by
  default, so this scraper never needed to set it.
- Added `withMeta=true` to every `/images` request in
  `get_images_by_filter()`. This is the single method backing both normal
  scraping and prompt mining, so the fix applies to both modes and to the GUI.
- Confirmed against the live API: before the fix, `meta` was `null` for
  every image (even top "Most Reactions" results with known prompts); after
  the fix, `meta` is populated as documented.

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

