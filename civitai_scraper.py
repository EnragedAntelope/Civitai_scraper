#!/usr/bin/env python3
"""
Civitai Image Prompt Scraper

Scrapes image prompts from Civitai based on model type.
"""

import requests
import json
import os
import re
import time
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import argparse


class CivitaiScraper:
    """Scraper for Civitai images and prompts."""

    BASE_URL = "https://civitai.com/api/v1"

    # Common banned word groups (used by GUI checkboxes)
    BANNED_CHARACTER_TAGS = [
        "1girl", "1woman", "1boy", "1man", "solo", "looking at viewer",
    ]
    BANNED_SCORING_TAGS = [
        "score_", "rating_",
    ]

    # Built-in presets for prompt mining
    # Note: banned_words here are subject-specific only;
    # character/scoring tags are handled separately via filter flags
    MINING_PRESETS = {
        "Custom": {
            "keywords": {},
            "required_words": [],
            "banned_words": [],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 1,
        },
        "Space / Sci-Fi": {
            "keywords": {
                "space": 1, "stars": 1, "galaxy": 1, "nebula": 2, "planet": 1,
                "spaceship": 2, "starship": 2, "cockpit": 2, "airlock": 2,
                "thruster": 2, "hull": 2, "zero-gravity": 3, "orbit": 2,
                "holographic": 1, "visor": 2, "corridor": 1, "engine": 1,
                "asteroid": 2, "sci-fi": 1, "futuristic": 1, "station": 1,
            },
            "required_words": [
                "space", "galaxy", "planet", "spaceship", "nebula",
                "orbit", "starship", "sci-fi", "stars",
            ],
            "banned_words": [
                "samurai", "tokyo", "geisha", "poptart",
                "fantasy", "magic", "sword", "witch", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Fantasy / Medieval": {
            "keywords": {
                "castle": 2, "knight": 2, "dragon": 3, "sword": 2, "shield": 1,
                "throne": 2, "kingdom": 2, "wizard": 2, "enchanted": 2, "mystical": 2,
                "dungeon": 2, "fortress": 2, "armor": 1, "tavern": 1, "medieval": 2,
                "fantasy": 1, "magic": 1, "ancient": 1, "mythical": 1,
            },
            "required_words": [
                "fantasy", "medieval", "castle", "dragon", "knight",
                "kingdom", "magic", "wizard",
            ],
            "banned_words": [
                "cyberpunk", "futuristic", "modern", "sci-fi",
                "spaceship", "robot", "neon", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Cyberpunk": {
            "keywords": {
                "neon": 2, "hologram": 2, "cybernetic": 3, "augmented": 2, "chrome": 2,
                "dystopian": 2, "megacity": 2, "hacker": 2, "implant": 2, "circuit": 1,
                "android": 2, "digital": 1, "rain": 1, "skyscraper": 1, "tech": 1,
                "cyberpunk": 1, "cyber": 1, "futuristic": 1,
            },
            "required_words": [
                "cyberpunk", "neon", "cyber", "futuristic",
                "dystopian", "chrome", "hologram",
            ],
            "banned_words": [
                "medieval", "fantasy", "pastoral",
                "forest", "cottage", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Nature / Landscape": {
            "keywords": {
                "mountain": 2, "forest": 2, "river": 1, "waterfall": 2, "sunset": 2,
                "aurora": 3, "canyon": 2, "meadow": 1, "ocean": 2, "valley": 2,
                "glacier": 2, "wilderness": 2, "clouds": 1, "lake": 1, "cliff": 1,
                "horizon": 1, "landscape": 1, "nature": 1, "scenery": 1,
            },
            "required_words": [
                "landscape", "nature", "mountain", "forest",
                "ocean", "sunset", "valley", "scenery",
            ],
            "banned_words": [
                "indoor", "room", "cyberpunk", "robot", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Architecture / Urban": {
            "keywords": {
                "building": 1, "skyscraper": 2, "cathedral": 2, "bridge": 2, "tower": 1,
                "facade": 2, "interior": 1, "dome": 2, "archway": 2, "columns": 1,
                "staircase": 1, "skyline": 2, "street": 1, "plaza": 1, "monument": 2,
                "brutalist": 2, "architecture": 1, "city": 1, "urban": 1,
            },
            "required_words": [
                "architecture", "building", "city", "urban",
                "skyline", "cathedral", "facade",
            ],
            "banned_words": [
                "nature", "forest", "animal", "fantasy", "magic", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Futuristic": {
            "keywords": {
                "futuristic": 2, "cyberpunk": 2, "sci-fi": 2, "high-tech": 2,
                "neon": 1, "hologram": 1, "mecha": 1, "android": 1,
                "spaceship": 1, "cybernetic": 1, "metropolis": 1, "utopian": 1,
                "sleek": 1, "advanced": 1, "chrome": 1, "laser": 1,
            },
            "required_words": ["futuristic", "sci-fi", "cyber", "tech", "future"],
            "banned_words": [
                "medieval", "historical", "ancient", "antique", "vintage",
                "retro", "steampunk", "fantasy", "magic", "wizard", "knight", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 3,
        },
        "Horror": {
            "keywords": {
                "horror": 2, "creepy": 2, "eerie": 2, "macabre": 2,
                "darkness": 1, "haunted": 1, "ghostly": 1, "lovecraftian": 1,
                "gothic": 1, "nightmare": 1, "skull": 1, "monster": 1,
                "abandoned": 1, "misty": 1, "blood": 1, "surreal": 1,
            },
            "required_words": ["horror", "scary", "dark", "creepy", "macabre"],
            "banned_words": [
                "cheerful", "bright", "sunny", "vibrant", "cute",
                "kawaii", "whimsical", "happy", "colorful", "pastel", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 3,
        },
        "Gigantism": {
            "keywords": {
                "colossal": 3, "monolithic": 3, "massive": 2, "towering": 2,
                "tiny human": 2, "scale comparison": 2, "megastructure": 3,
                "looming": 2, "immense": 1, "cyclopean": 3, "titan": 2,
                "silhouette in distance": 2, "vast landscape": 1, "dwarf": 1,
            },
            "required_words": ["colossal", "massive", "giant", "scale", "monolith", "tiny"],
            "banned_words": [
                "portrait", "close-up", "selfie", "headshot", "macro",
                "intimate", "crowd", "bust shot", "looking at viewer", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 3,
        },
        "Micro-World": {
            "keywords": {
                "miniature": 3, "macro photography": 2, "diorama": 3, "tilt-shift": 2,
                "tiny world": 2, "inside a": 2, "microscopic": 1, "scale": 1,
                "living inside": 2, "pocket-sized": 2, "tabletop": 1, "small scale": 1,
            },
            "required_words": ["miniature", "macro", "diorama", "tiny", "inside", "small"],
            "banned_words": [
                "giant", "colossal", "massive", "landscape", "mountain",
                "skyline", "outer space", "buzz",
            ],
            "min_length": 60,
            "max_commas": 25,
            "min_score": 3,
        },
        "Retro-Futuristic": {
            "keywords": {
                "retro-futuristic": 3, "atompunk": 3, "raypunk": 3, "cassette-futurism": 2,
                "mid-century modern": 2, "googie": 3, "vacuum tubes": 2, "analog tech": 1,
                "vintage space": 1, "rocketship": 1, "bubble-top": 2, "bakelite": 2,
                "chrome fins": 2, "1950s": 1, "1960s": 1, "fallout-style": 1,
            },
            "required_words": [
                "retro", "atompunk", "raypunk", "vintage", "analog", "mid-century", "googie",
            ],
            "banned_words": [
                "cybernetic", "hologram", "modern", "smartphone", "contemporary",
                "digital", "flat design", "buzz", "sleek white", "high-tech",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 3,
        },
        "Underwater": {
            "keywords": {
                "underwater": 3, "ocean": 2, "coral": 2, "reef": 2, "deep sea": 3,
                "bioluminescent": 3, "submarine": 2, "aquatic": 2, "seabed": 2,
                "kelp": 1, "bubbles": 1, "diving": 1, "fish": 1, "whale": 2,
                "abyss": 2, "trench": 2, "jellyfish": 2, "shipwreck": 2,
            },
            "required_words": [
                "underwater", "ocean", "sea", "aquatic", "coral", "deep",
            ],
            "banned_words": [
                "desert", "mountain", "sky", "flying", "space", "forest", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Steampunk": {
            "keywords": {
                "steampunk": 3, "clockwork": 2, "brass": 2, "gears": 2, "steam": 2,
                "victorian": 2, "airship": 2, "goggles": 1, "mechanical": 1,
                "pipes": 1, "copper": 1, "cog": 1, "dirigible": 2, "boiler": 1,
                "pneumatic": 2, "rivets": 1,
            },
            "required_words": [
                "steampunk", "clockwork", "brass", "gears", "steam", "victorian",
            ],
            "banned_words": [
                "cyberpunk", "neon", "hologram", "digital", "modern",
                "smartphone", "laser", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
        "Post-Apocalyptic": {
            "keywords": {
                "post-apocalyptic": 3, "wasteland": 2, "ruins": 2, "desolate": 2,
                "survivor": 2, "overgrown": 2, "abandoned": 2, "bunker": 2,
                "rubble": 1, "decay": 1, "scavenger": 2, "fallout": 2,
                "barren": 1, "dust": 1, "collapsed": 1, "rusty": 1,
            },
            "required_words": [
                "post-apocalyptic", "wasteland", "ruins", "abandoned", "desolate", "survivor",
            ],
            "banned_words": [
                "pristine", "luxury", "modern", "clean", "polished",
                "utopian", "cheerful", "buzz",
            ],
            "min_length": 50,
            "max_commas": 20,
            "min_score": 2,
        },
    }

    def __init__(self, output_dir: str = "output", delay: float = 1.0, api_key: str = None):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped data
            delay: Delay between API requests in seconds
            api_key: Optional Civitai API key for authenticated requests
        """
        self.output_dir = output_dir
        self.delay = delay
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Add API key to headers if provided
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def get_models(self,
                   model_type: Optional[str] = None,
                   base_model: Optional[str] = None,
                   limit: int = 100,
                   page: int = 1,
                   sort: str = "Highest Rated") -> Dict:
        """
        Get models from Civitai API.

        Args:
            model_type: Type of model (Checkpoint, LORA, TextualInversion, Hypernetwork, etc.)
            base_model: Base model architecture (SD 1.5, SDXL, Flux, Pony, etc.)
            limit: Number of results per page (max 100)
            page: Page number
            sort: Sort order (Highest Rated, Most Downloaded, Newest)

        Returns:
            API response with models data
        """
        url = f"{self.BASE_URL}/models"
        params = {
            "limit": min(limit, 100),
            "page": page,
            "sort": sort
        }

        if model_type:
            params["types"] = model_type

        if base_model:
            params["baseModels"] = base_model

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching models: {e}")
            return {"items": [], "metadata": {}}

    def get_images_by_filter(self,
                            base_model: Optional[str] = None,
                            model_type: Optional[str] = None,
                            limit: int = 100,
                            page: int = 1,
                            sort: str = "Most Reactions",
                            period: Optional[str] = None,
                            nsfw: Optional[str] = None,
                            username: Optional[str] = None,
                            model_id: Optional[int] = None,
                            model_version_id: Optional[int] = None,
                            post_id: Optional[int] = None,
                            cursor: Optional[str] = None) -> Dict:
        """
        Get images directly from the images API endpoint.

        Args:
            base_model: Base model architecture filter
            model_type: Model type filter
            limit: Number of results per page (max 200)
            page: Page number (used only if cursor is not provided)
            sort: Sort order (Most Reactions, Most Comments, Newest)
            period: Time period filter (AllTime, Year, Month, Week, Day)
            nsfw: NSFW filter (None, Soft, Mature, X)
            username: Filter by creator username
            model_id: Filter by model ID
            model_version_id: Filter by model version ID
            post_id: Filter by post ID
            cursor: Cursor for pagination (overrides page if provided)

        Returns:
            API response with images data (includes metadata.nextCursor)
        """
        url = f"{self.BASE_URL}/images"
        params = {
            "limit": min(limit, 200),
            "sort": sort
        }

        # Use cursor-based pagination if available, else page-based
        if cursor:
            params["cursor"] = cursor
        else:
            params["page"] = page

        if base_model:
            params["baseModels"] = base_model  # Note: API uses plural "baseModels"

        if period:
            params["period"] = period

        if nsfw:
            params["nsfw"] = nsfw

        if username:
            params["username"] = username

        if model_id:
            params["modelId"] = model_id

        if model_version_id:
            params["modelVersionId"] = model_version_id

        if post_id:
            params["postId"] = post_id

        try:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching images: {e}")
            return {"items": [], "metadata": {}}

    def process_image_data(self, image: Dict) -> Dict:
        """
        Process raw image data from API into our format.

        Args:
            image: Raw image data from API

        Returns:
            Processed image data
        """
        # Handle case where meta might be None
        meta = image.get("meta") or {}

        return {
            "image_id": image.get("id"),
            "image_url": image.get("url"),
            "width": image.get("width"),
            "height": image.get("height"),
            "base_model": image.get("baseModel"),
            "created_at": image.get("createdAt"),
            "username": image.get("username"),
            "post_id": image.get("postId"),
            "model_version_ids": image.get("modelVersionIds") or [],
            "prompt": meta.get("prompt") if isinstance(meta, dict) else None,
            "negative_prompt": meta.get("negativePrompt") if isinstance(meta, dict) else None,
            "seed": meta.get("seed") if isinstance(meta, dict) else None,
            "steps": meta.get("steps") if isinstance(meta, dict) else None,
            "sampler": meta.get("sampler") if isinstance(meta, dict) else None,
            "cfg_scale": meta.get("cfgScale") if isinstance(meta, dict) else None,
            "size": meta.get("Size") if isinstance(meta, dict) else None,
            "model_hash": meta.get("Model hash") if isinstance(meta, dict) else None,
            "hashes": meta.get("hashes") if isinstance(meta, dict) else None,
            "resources": meta.get("resources", []) if isinstance(meta, dict) else []
        }

    def scrape_by_base_model(self,
                            base_model: Optional[str] = None,
                            model_type: Optional[str] = None,
                            max_images: int = 100,
                            sort: str = "Most Reactions",
                            strict_filter: bool = True,
                            period: Optional[str] = None,
                            nsfw: Optional[str] = None,
                            username: Optional[str] = None,
                            model_id: Optional[int] = None,
                            model_version_id: Optional[int] = None,
                            post_id: Optional[int] = None) -> List[Dict]:
        """
        Scrape prompts, optionally filtered by base model architecture.

        Args:
            base_model: Base model architecture to scrape (e.g., 'SDXL 1.0', 'Pony'). None for all.
            model_type: Optional model type filter (Checkpoint, LORA, etc.)
            max_images: Maximum number of images to scrape
            sort: Sort order (Most Reactions, Most Comments, Newest)
            strict_filter: If True and base_model specified, only include exact matches
            period: Time period filter (AllTime, Year, Month, Week, Day)
            nsfw: NSFW filter (None, Soft, Mature, X)
            username: Filter by creator username
            model_id: Filter by model ID
            model_version_id: Filter by model version ID
            post_id: Filter by post ID

        Returns:
            List of all scraped image data with prompts
        """
        filter_desc = base_model or "All base models"
        if model_type:
            filter_desc += f" ({model_type})"
        print(f"Scraping images for {filter_desc}...")
        print(f"Target: {max_images} images")
        if strict_filter and base_model:
            print(f"Strict filtering: Only images with base_model='{base_model}'")

        all_images = []
        cursor = None
        pages_fetched = 0
        images_per_page = min(200, max_images * 3 if strict_filter else max_images)
        pages_without_results = 0
        max_empty_pages = 5

        while len(all_images) < max_images:
            pages_fetched += 1
            print(f"Fetching page {pages_fetched}... (currently have {len(all_images)} images)")

            images_data = self.get_images_by_filter(
                base_model=base_model,
                model_type=model_type,
                limit=min(200, images_per_page),
                sort=sort,
                period=period,
                nsfw=nsfw,
                username=username,
                model_id=model_id,
                model_version_id=model_version_id,
                post_id=post_id,
                cursor=cursor,
            )

            items = images_data.get("items", [])
            if not items:
                print("No more images found.")
                break

            added_this_page = 0
            for image in items:
                if len(all_images) >= max_images:
                    break

                processed_image = self.process_image_data(image)

                if strict_filter and base_model:
                    if processed_image.get('base_model') == base_model:
                        all_images.append(processed_image)
                        added_this_page += 1
                else:
                    all_images.append(processed_image)
                    added_this_page += 1

            if strict_filter and base_model:
                print(f"  Matched {added_this_page} out of {len(items)} images")
                if added_this_page == 0:
                    pages_without_results += 1
                else:
                    pages_without_results = 0

                if pages_without_results >= max_empty_pages:
                    print(f"No matching images found in {max_empty_pages} consecutive pages. Stopping.")
                    break
            else:
                print(f"  Added {added_this_page} images")

            # Cursor-based pagination
            metadata = images_data.get("metadata", {})
            cursor = metadata.get("nextCursor")
            if not cursor:
                print("Reached last page.")
                break

            time.sleep(self.delay)

        print(f"Scraped {len(all_images)} images")
        if all_images:
            actual_base_models = set(img.get('base_model') for img in all_images)
            if len(actual_base_models) > 1 or not base_model:
                print(f"Base models in results: {actual_base_models}")
        return all_images

    def save_results(self, data: List[Dict], filename: str = None,
                     filename_prefix: str = None):
        """
        Save scraped data to JSON file.

        Args:
            data: List of scraped image data
            filename: Output filename (auto-generated if None)
            filename_prefix: Optional prefix prepended to auto-generated name
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"{self.sanitize_filename_prefix(filename_prefix)}_" if filename_prefix else ""
            filename = f"{prefix}civitai_prompts_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filepath}")

    def export_prompts_only(self, data: List[Dict], filename: str = None,
                           double_spaced: bool = False, use_separator: bool = False,
                           positive_only: bool = False, one_per_line: bool = False,
                           filename_prefix: str = None):
        """
        Export only prompts to a text file.

        Args:
            data: List of scraped image data
            filename: Output filename (auto-generated if None)
            double_spaced: If True, add extra blank line between prompts
            use_separator: If True, use visual separator line instead of blank lines
            positive_only: If True, skip negative prompts in output
            one_per_line: If True, clean and collapse each prompt to a single line
                          with no separators (overrides double_spaced and use_separator)
            filename_prefix: Optional prefix prepended to auto-generated name
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"{self.sanitize_filename_prefix(filename_prefix)}_" if filename_prefix else ""
            filename = f"{prefix}prompts_only_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)

        # Define separator - characters unlikely to appear in prompts
        separator = "─" * 50  # Unicode box-drawing character

        with open(filepath, 'w', encoding='utf-8') as f:
            prompts_written = 0
            total_with_prompts = sum(1 for d in data if d.get("prompt"))

            for item in data:
                if item.get("prompt"):
                    prompt_text = item.get("prompt")

                    if one_per_line:
                        # Clean format: one cleaned prompt per line, no extras
                        prompt_text = self.clean_prompt(prompt_text)
                        f.write(f"{prompt_text}\n")
                    else:
                        # Standard format
                        f.write(f"{prompt_text}\n")
                        if not positive_only and item.get("negative_prompt"):
                            f.write(f"[NEGATIVE]: {item.get('negative_prompt')}\n")

                    prompts_written += 1

                    # Add spacing/separator (not after last, not in one_per_line mode)
                    if not one_per_line and prompts_written < total_with_prompts:
                        if use_separator:
                            f.write(f"\n{separator}\n\n")
                        elif double_spaced:
                            f.write("\n\n")
                        else:
                            f.write("\n")

        print(f"Prompts exported to {filepath}")

    @staticmethod
    def sanitize_filename_prefix(name: str, max_len: int = 30) -> str:
        """Sanitize a preset/label name for use as a filename prefix.

        Replaces illegal filename characters, collapses whitespace to
        underscores, and truncates to *max_len* characters.
        """
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'[\s/]+', '_', sanitized)
        sanitized = sanitized.strip('_.')
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len].rstrip('_')
        return sanitized

    @staticmethod
    def clean_prompt(raw: str) -> str:
        """
        Clean a raw prompt by removing LoRA/embedding tags, weight syntax, and stray brackets.

        Args:
            raw: Raw prompt string from image metadata

        Returns:
            Cleaned prompt string
        """
        clean = raw.replace('\n', ' ')
        # Remove <lora:...> and <embedding:...> tags
        clean = re.sub(r"<(lora|embedding):[^>]*>", "", clean)
        # Remove weight syntax like (word:1.2) -> word
        clean = re.sub(r"\(([^:]+):[0-9.]+\)", r"\1", clean)
        # Remove stray brackets
        clean = re.sub(r"[\(\)\[\]]", "", clean)
        # Collapse whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @staticmethod
    def evaluate_prompt(prompt: str, keywords: Dict[str, int],
                        required_words: List[str], banned_words: List[str],
                        min_length: int = 100, max_commas: int = 15,
                        min_score: int = 3) -> Tuple[bool, int]:
        """
        Evaluate a prompt against quality criteria.

        Args:
            prompt: Cleaned prompt string
            keywords: Dict of keyword -> weight for scoring
            required_words: At least one must appear
            banned_words: Any appearance causes instant rejection
            min_length: Minimum character length
            max_commas: Maximum comma count (filters tag-soup prompts)
            min_score: Minimum keyword score to pass

        Returns:
            Tuple of (passes: bool, score: int)
        """
        p_lower = prompt.lower()

        # Filter: minimum length
        if len(prompt) < min_length:
            return False, 0

        # Filter: banned words (instant rejection)
        for bad in banned_words:
            if bad.lower() in p_lower:
                return False, 0

        # Filter: required words (at least one must appear)
        # If no required words specified, fall back to keyword list
        check_words = required_words if required_words else list(keywords.keys())
        if check_words:
            if not any(word.lower() in p_lower for word in check_words):
                return False, 0

        # Filter: tag-soup detection (too many commas)
        if p_lower.count(",") > max_commas:
            return False, 0

        # Score against weighted keywords
        score = 0
        for word, points in keywords.items():
            if word.lower() in p_lower:
                score += points

        return score >= min_score, score

    def mine_prompts(self, keywords: Dict[str, int],
                     required_words: List[str], banned_words: List[str],
                     min_length: int = 100, max_commas: int = 15,
                     min_score: int = 3, target_count: int = 50,
                     sort: str = "Newest", period: Optional[str] = None,
                     nsfw: Optional[str] = None,
                     base_model: Optional[str] = None,
                     is_running_callback=None,
                     log_callback=None) -> List[Tuple[str, int]]:
        """
        Mine prompts from Civitai images using content-based scoring.

        Scans through images and evaluates each prompt against the given
        criteria, returning high-quality matches for the specified subject.

        Args:
            keywords: Dict of keyword -> weight for scoring
            required_words: At least one must appear in prompt
            banned_words: Any appearance causes instant rejection
            min_length: Minimum prompt character length
            max_commas: Maximum comma count (filters tag-soup)
            min_score: Minimum keyword score threshold
            target_count: Number of matching prompts to find
            sort: Sort order for scanning (Newest, Most Reactions, Most Comments)
            nsfw: NSFW filter (None, Soft, Mature, X)
            base_model: Optional base model filter
            is_running_callback: Callable returning bool, checked each iteration
            log_callback: Callable for logging progress messages

        Returns:
            List of (cleaned_prompt, score) tuples sorted by score descending
        """
        def _log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        def _is_running():
            if is_running_callback:
                return is_running_callback()
            return True

        found_prompts: Set[str] = set()
        results: List[Tuple[str, int]] = []
        cursor = None
        pages_fetched = 0
        scanned = 0
        max_pages = 200  # Safety limit

        _log(f"Mining for {target_count} matching prompts...")
        _log(f"Scanning by '{sort}' with {len(keywords)} weighted keywords")
        _log(f"Filters: min_length={min_length}, max_commas={max_commas}, min_score={min_score}")
        _log("")

        while len(results) < target_count and _is_running() and pages_fetched < max_pages:
            images_data = self.get_images_by_filter(
                base_model=base_model,
                limit=200,
                sort=sort,
                period=period,
                nsfw=nsfw,
                cursor=cursor,
            )

            items = images_data.get("items", [])
            if not items:
                _log("No more images available from API.")
                break

            pages_fetched += 1

            for item in items:
                if len(results) >= target_count or not _is_running():
                    break

                scanned += 1
                meta = item.get("meta") or {}
                raw_prompt = meta.get("prompt", "") if isinstance(meta, dict) else ""

                if not raw_prompt:
                    continue

                cleaned = self.clean_prompt(raw_prompt)
                passes, score = self.evaluate_prompt(
                    cleaned, keywords, required_words, banned_words,
                    min_length, max_commas, min_score
                )

                if passes and cleaned not in found_prompts:
                    found_prompts.add(cleaned)
                    results.append((cleaned, score))
                    _log(f"[MATCH #{len(results)}] Score: {score} | Scanned: {scanned}")
                    _log(f"  {cleaned[:120]}...")

            _log(f"Page {pages_fetched} done. Scanned {scanned} images, found {len(results)} matches.")

            # Cursor-based pagination
            metadata = images_data.get("metadata", {})
            cursor = metadata.get("nextCursor")
            if not cursor:
                _log("Reached last available page.")
                break

            time.sleep(self.delay)

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def save_mined_json(self, prompts: List[Tuple[str, int]], filename: str = None,
                        filename_prefix: str = None):
        """
        Save mined prompts to a JSON file.

        Args:
            prompts: List of (prompt, score) tuples
            filename: Output filename (auto-generated if None)
            filename_prefix: Optional prefix prepended to auto-generated name
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"{self.sanitize_filename_prefix(filename_prefix)}_" if filename_prefix else ""
            filename = f"{prefix}mined_prompts_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)
        data = [{"prompt": prompt, "score": score} for prompt, score in prompts]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Mined prompts saved to {filepath}")

    def export_mined_prompts(self, prompts: List[Tuple[str, int]],
                             filename: str = None,
                             use_separator: bool = True,
                             one_per_line: bool = False,
                             filename_prefix: str = None):
        """
        Export mined prompts to a text file.

        Args:
            prompts: List of (prompt, score) tuples
            filename: Output filename (auto-generated if None)
            use_separator: Use visual separator lines between prompts
            one_per_line: If True, write one prompt per line with no spacing
                          (overrides use_separator)
            filename_prefix: Optional prefix prepended to auto-generated name
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"{self.sanitize_filename_prefix(filename_prefix)}_" if filename_prefix else ""
            filename = f"{prefix}mined_prompts_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)
        separator = "\u2500" * 50  # Unicode box-drawing character

        with open(filepath, 'w', encoding='utf-8') as f:
            for i, (prompt, score) in enumerate(prompts):
                f.write(f"{prompt}\n")

                # Add separator between prompts (not after the last one)
                if not one_per_line and i < len(prompts) - 1:
                    if use_separator:
                        f.write(f"\n{separator}\n\n")
                    else:
                        f.write("\n")

        print(f"Mined prompts exported to {filepath}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Scrape image prompts from Civitai")
    parser.add_argument(
        "--base-model",
        type=str,
        default=None,
        help="Base model architecture (e.g., 'SD 1.5', 'SDXL 1.0', 'Pony', 'Flux.1 D'). Omit for all models."
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["Checkpoint", "LORA", "LoCon", "TextualInversion", "Hypernetwork",
                 "AestheticGradient", "Controlnet", "Poses"],
        help="Optional: Filter by model type"
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=100,
        help="Maximum number of images to scrape (default: 100)"
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="Most Reactions",
        choices=["Most Reactions", "Most Comments", "Newest"],
        help="Sort order for images (default: Most Reactions)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for scraped data (default: output)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--export-prompts",
        action="store_true",
        help="Also export prompts to a separate text file"
    )
    parser.add_argument(
        "--double-spaced",
        action="store_true",
        help="Use double line spacing in exported prompts file"
    )
    parser.add_argument(
        "--no-strict-filter",
        action="store_true",
        help="Disable strict base model filtering (include mixed results)"
    )
    parser.add_argument(
        "--period",
        type=str,
        choices=["AllTime", "Year", "Month", "Week", "Day"],
        help="Time period filter for images"
    )
    parser.add_argument(
        "--nsfw",
        type=str,
        choices=["None", "Soft", "Mature", "X"],
        help="NSFW content filter (None=SFW only, X=all NSFW levels)"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Filter by creator username"
    )
    parser.add_argument(
        "--model-id",
        type=int,
        help="Filter by specific model ID"
    )
    parser.add_argument(
        "--model-version-id",
        type=int,
        help="Filter by specific model version ID"
    )
    parser.add_argument(
        "--post-id",
        type=int,
        help="Filter by specific post ID"
    )
    parser.add_argument(
        "--use-separator",
        action="store_true",
        help="Use visual separator lines between prompts instead of blank lines"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Civitai API key for authenticated features (favorites, hidden models)"
    )

    # Prompt mining arguments
    parser.add_argument(
        "--mine",
        action="store_true",
        help="Enable prompt mining mode (find best prompts for a subject)"
    )
    parser.add_argument(
        "--mine-preset",
        type=str,
        choices=list(CivitaiScraper.MINING_PRESETS.keys()),
        help="Use a built-in mining preset"
    )
    parser.add_argument(
        "--mine-keywords",
        type=str,
        help="Comma-separated keyword:weight pairs (e.g., 'cockpit:2,thruster:3')"
    )
    parser.add_argument(
        "--mine-required",
        type=str,
        help="Comma-separated required words (at least one must appear)"
    )
    parser.add_argument(
        "--mine-banned",
        type=str,
        help="Comma-separated banned words (instant rejection)"
    )
    parser.add_argument(
        "--mine-min-length",
        type=int,
        default=100,
        help="Minimum prompt length for mining (default: 100)"
    )
    parser.add_argument(
        "--mine-max-commas",
        type=int,
        default=15,
        help="Maximum commas in prompt for mining (default: 15)"
    )
    parser.add_argument(
        "--mine-min-score",
        type=int,
        default=3,
        help="Minimum keyword score for mining (default: 3)"
    )
    parser.add_argument(
        "--mine-target",
        type=int,
        default=50,
        help="Number of matching prompts to find (default: 50)"
    )

    args = parser.parse_args()

    # Initialize scraper
    scraper = CivitaiScraper(output_dir=args.output_dir, delay=args.delay, api_key=args.api_key)

    if args.mine:
        # Prompt mining mode
        keywords = {}
        required_words = []
        banned_words = []
        min_length = args.mine_min_length
        max_commas = args.mine_max_commas
        min_score = args.mine_min_score

        # Load preset if specified
        if args.mine_preset and args.mine_preset in CivitaiScraper.MINING_PRESETS:
            preset = CivitaiScraper.MINING_PRESETS[args.mine_preset]
            keywords = dict(preset["keywords"])
            required_words = list(preset["required_words"])
            banned_words = list(preset["banned_words"])
            min_length = preset["min_length"]
            max_commas = preset["max_commas"]
            min_score = preset["min_score"]

        # Override with custom values if provided
        if args.mine_keywords:
            for pair in args.mine_keywords.split(","):
                pair = pair.strip()
                if ":" in pair:
                    word, weight = pair.rsplit(":", 1)
                    keywords[word.strip()] = int(weight.strip())

        if args.mine_required:
            required_words = [w.strip() for w in args.mine_required.split(",") if w.strip()]

        if args.mine_banned:
            banned_words = [w.strip() for w in args.mine_banned.split(",") if w.strip()]

        if not keywords:
            print("Error: No keywords specified. Use --mine-preset or --mine-keywords.")
            return

        results = scraper.mine_prompts(
            keywords=keywords,
            required_words=required_words,
            banned_words=banned_words,
            min_length=min_length,
            max_commas=max_commas,
            min_score=min_score,
            target_count=args.mine_target,
            sort=args.sort,
            period=args.period,
            nsfw=args.nsfw,
            base_model=args.base_model,
        )

        if results:
            scraper.export_mined_prompts(results, use_separator=args.use_separator)
            print(f"\nMining completed! Found {len(results)} matching prompts.")
        else:
            print("\nNo matching prompts found.")
    else:
        # Normal scraping mode
        results = scraper.scrape_by_base_model(
            base_model=args.base_model,
            model_type=args.model_type,
            max_images=args.max_images,
            sort=args.sort,
            strict_filter=not args.no_strict_filter,
            period=args.period,
            nsfw=args.nsfw,
            username=args.username,
            model_id=args.model_id,
            model_version_id=args.model_version_id,
            post_id=args.post_id
        )

        # Save results
        scraper.save_results(results)

        # Export prompts if requested
        if args.export_prompts:
            scraper.export_prompts_only(results, double_spaced=args.double_spaced,
                                        use_separator=args.use_separator)

        print("\nScraping completed!")
        print(f"Total images scraped: {len(results)}")
        print(f"Images with prompts: {sum(1 for r in results if r.get('prompt'))}")


if __name__ == "__main__":
    main()
