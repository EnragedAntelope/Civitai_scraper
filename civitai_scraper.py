#!/usr/bin/env python3
"""
Civitai Image Prompt Scraper

Scrapes image prompts from Civitai based on model type.
"""

import requests
import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime
import argparse


class CivitaiScraper:
    """Scraper for Civitai images and prompts."""

    BASE_URL = "https://civitai.com/api/v1"

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
                            post_id: Optional[int] = None) -> Dict:
        """
        Get images directly from the images API endpoint.

        Args:
            base_model: Base model architecture filter
            model_type: Model type filter
            limit: Number of results per page (max 200)
            page: Page number
            sort: Sort order (Most Reactions, Most Comments, Newest)
            period: Time period filter (AllTime, Year, Month, Week, Day)
            nsfw: NSFW filter (None, Soft, Mature, X)
            username: Filter by creator username
            model_id: Filter by model ID
            model_version_id: Filter by model version ID
            post_id: Filter by post ID

        Returns:
            API response with images data
        """
        url = f"{self.BASE_URL}/images"
        params = {
            "limit": min(limit, 200),
            "page": page,
            "sort": sort
        }

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
        page = 1
        images_per_page = min(200, max_images * 3 if strict_filter else max_images)  # Fetch more if filtering
        pages_without_results = 0
        max_empty_pages = 5  # Stop if we get 5 pages with no matching results

        while len(all_images) < max_images:
            print(f"Fetching page {page}... (currently have {len(all_images)} images)")

            images_data = self.get_images_by_filter(
                base_model=base_model,
                model_type=model_type,
                limit=min(200, images_per_page),
                page=page,
                sort=sort,
                period=period,
                nsfw=nsfw,
                username=username,
                model_id=model_id,
                model_version_id=model_version_id,
                post_id=post_id
            )

            items = images_data.get("items", [])
            if not items:
                print("No more images found.")
                break

            # Process each image
            added_this_page = 0
            for image in items:
                if len(all_images) >= max_images:
                    break

                processed_image = self.process_image_data(image)

                # Apply strict filtering only if base_model is specified and strict_filter is True
                if strict_filter and base_model:
                    # Only include if base_model matches exactly
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

                # Stop if we've had too many pages without results
                if pages_without_results >= max_empty_pages:
                    print(f"No matching images found in {max_empty_pages} consecutive pages. Stopping.")
                    break
            else:
                print(f"  Added {added_this_page} images")

            page += 1
            time.sleep(self.delay)

            # Check if we've reached the end
            metadata = images_data.get("metadata", {})
            if metadata.get("currentPage") >= metadata.get("totalPages", 1):
                print("Reached last page.")
                break

        print(f"Scraped {len(all_images)} images")
        if all_images:
            actual_base_models = set(img.get('base_model') for img in all_images)
            if len(actual_base_models) > 1 or not base_model:
                print(f"Base models in results: {actual_base_models}")
        return all_images

    def save_results(self, data: List[Dict], filename: str = None):
        """
        Save scraped data to JSON file.

        Args:
            data: List of scraped image data
            filename: Output filename (auto-generated if None)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"civitai_prompts_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filepath}")

    def export_prompts_only(self, data: List[Dict], filename: str = None,
                           double_spaced: bool = False, use_separator: bool = False):
        """
        Export only prompts to a text file.

        Args:
            data: List of scraped image data
            filename: Output filename (auto-generated if None)
            double_spaced: If True, add extra blank line between prompts
            use_separator: If True, use visual separator line instead of blank lines
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prompts_only_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)

        # Define separator - characters unlikely to appear in prompts
        separator = "─" * 50  # Unicode box-drawing character

        with open(filepath, 'w', encoding='utf-8') as f:
            for i, item in enumerate(data):
                if item.get("prompt"):
                    # Write prompt
                    f.write(f"{item.get('prompt')}\n")
                    # Write negative prompt if exists
                    if item.get("negative_prompt"):
                        f.write(f"[NEGATIVE]: {item.get('negative_prompt')}\n")

                    # Add spacing/separator between prompts (not after the last one)
                    if i < len([d for d in data if d.get("prompt")]) - 1:
                        if use_separator:
                            f.write(f"\n{separator}\n\n")
                        elif double_spaced:
                            f.write("\n\n")  # Two blank lines for double spacing
                        else:
                            f.write("\n")  # One blank line between prompts

        print(f"Prompts exported to {filepath}")


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

    args = parser.parse_args()

    # Initialize scraper
    scraper = CivitaiScraper(output_dir=args.output_dir, delay=args.delay, api_key=args.api_key)

    # Scrape data
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
