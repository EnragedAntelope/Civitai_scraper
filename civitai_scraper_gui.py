#!/usr/bin/env python3
"""
Civitai Image Prompt Scraper GUI

Cross-platform GUI for scraping image prompts from Civitai.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
from datetime import datetime
from civitai_scraper import CivitaiScraper


class CivitaiScraperGUI:
    """GUI for Civitai scraper."""

    # Common base models from the Civitai interface
    # Note: "Any" allows scraping without base model filter
    # New models can be added here as Civitai introduces them
    BASE_MODELS = [
        "Any",  # No filter - get all base models
        "Flux.1 D",
        "Flux.1 S",
        "Flux.2 D",
        "Illustrious",
        "Nano Banana",
        "NoobAI",
        "Other",
        "Pony",
        "SD 1.5",
        "SDXL 1.0",
        "ZImageTurbo",
        # Legacy/Less common models
        "SD 1.5 LCM",
        "SD 1.5 Hyper",
        "SD 2.0",
        "SD 2.1",
        "SDXL 1.0 LCM",
        "SDXL Turbo",
        "SDXL Lightning",
        "SDXL Hyper",
        "SDXL Distilled",
        "Pony V7",
        "AuraFlow",
        "Chroma",
        "CogVideoX",
        "HiDream",
        "Hunyuan 1",
        "Hunyuan Video",
        "Kolors",
        "LTXV",
        "Lumina",
        "Mochi",
        "PixArt a",
        "PixArt E",
        "Qwen",
        "Wan Video 1.3B v2v",
        "Wan Video 14B v2v",
        "Wan Video 14B v2v 480p",
        "Wan Video 14B v2v 720p",
        "Wan Video 2.2 T2V-SB",
        "Wan Video 2.2 I2V-A14B",
        "Wan Video 2.2 T2V-A14B",
        "Wan Video 2.5 T2V",
        "Wan Video 2.5 I2V",
    ]

    MODEL_TYPES = [
        "Any",
        "Checkpoint",
        "LORA",
        "LoCon",
        "TextualInversion",
        "Hypernetwork",
        "AestheticGradient",
        "Controlnet",
        "Poses"
    ]

    SORT_OPTIONS = [
        "Most Reactions",
        "Most Comments",
        "Newest"
    ]

    PERIOD_OPTIONS = [
        "AllTime",
        "Year",
        "Month",
        "Week",
        "Day"
    ]

    NSFW_OPTIONS = [
        "Any",       # No filter
        "None",      # SFW only
        "Soft",      # Include soft NSFW
        "Mature",    # Include mature
        "X"          # Include all NSFW
    ]

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Civitai Image Prompt Scraper")
        self.root.geometry("700x700")
        self.root.minsize(600, 500)

        # Make window resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Variables
        self.is_scraping = False
        self.scraper = None

        # Create scrollable container
        self.setup_scrollable_frame()

        # Create UI
        self.create_widgets()

    def setup_scrollable_frame(self):
        """Set up a scrollable frame with auto-hiding scrollbar."""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Create frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind events
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        """Update scroll region and show/hide scrollbar."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()

    def _on_canvas_configure(self, event):
        """Resize frame to match canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._update_scrollbar_visibility()

    def _update_scrollbar_visibility(self):
        """Show scrollbar only when content exceeds visible area."""
        self.root.update_idletasks()
        if self.scrollable_frame.winfo_reqheight() > self.canvas.winfo_height():
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if self.scrollable_frame.winfo_reqheight() > self.canvas.winfo_height():
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding (inside scrollable frame)
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Civitai Image Prompt Scraper",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Base Model
        row = 1
        ttk.Label(main_frame, text="Base Model:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.base_model_var = tk.StringVar(value="Any")
        base_model_combo = ttk.Combobox(
            main_frame,
            textvariable=self.base_model_var,
            values=self.BASE_MODELS,
            state="readonly",
            width=30
        )
        base_model_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="('Any' = all models)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Model Type
        row += 1
        ttk.Label(main_frame, text="Model Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_type_var = tk.StringVar(value="Any")
        model_type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_type_var,
            values=self.MODEL_TYPES,
            state="readonly",
            width=30
        )
        model_type_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(Optional)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Max Images
        row += 1
        ttk.Label(main_frame, text="Max Images:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_images_var = tk.IntVar(value=100)
        max_images_spinbox = ttk.Spinbox(
            main_frame,
            from_=1,
            to=10000,
            textvariable=self.max_images_var,
            width=28
        )
        max_images_spinbox.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        # Sort Order
        row += 1
        ttk.Label(main_frame, text="Sort By:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sort_var = tk.StringVar(value="Most Reactions")
        sort_combo = ttk.Combobox(
            main_frame,
            textvariable=self.sort_var,
            values=self.SORT_OPTIONS,
            state="readonly",
            width=30
        )
        sort_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        # Time Period Filter
        row += 1
        ttk.Label(main_frame, text="Time Period:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.period_var = tk.StringVar(value="AllTime")
        period_combo = ttk.Combobox(
            main_frame,
            textvariable=self.period_var,
            values=self.PERIOD_OPTIONS,
            state="readonly",
            width=30
        )
        period_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(Filter by date)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # NSFW Filter
        row += 1
        ttk.Label(main_frame, text="NSFW Filter:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.nsfw_var = tk.StringVar(value="Any")
        nsfw_combo = ttk.Combobox(
            main_frame,
            textvariable=self.nsfw_var,
            values=self.NSFW_OPTIONS,
            state="readonly",
            width=30
        )
        nsfw_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(None=SFW only)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Username Filter
        row += 1
        ttk.Label(main_frame, text="Username:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value="")
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        username_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(Filter by creator)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Delay
        row += 1
        ttk.Label(main_frame, text="Delay (seconds):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        delay_spinbox = ttk.Spinbox(
            main_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.delay_var,
            width=28
        )
        delay_spinbox.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(Rate limiting)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Output Directory
        row += 1
        ttk.Label(main_frame, text="Output Directory:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value="output")
        output_dir_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var)
        output_dir_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        browse_button = ttk.Button(main_frame, text="Browse...", command=self.browse_output_dir)
        browse_button.grid(row=row, column=2, sticky=tk.W, padx=(5, 0))

        # Export Prompts Checkbox
        row += 1
        self.export_prompts_var = tk.BooleanVar(value=False)
        export_check = ttk.Checkbutton(
            main_frame,
            text="Export prompts to separate text file",
            variable=self.export_prompts_var
        )
        export_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Double Spaced Checkbox
        row += 1
        self.double_spaced_var = tk.BooleanVar(value=False)
        double_spaced_check = ttk.Checkbutton(
            main_frame,
            text="Use double line spacing in prompts file",
            variable=self.double_spaced_var
        )
        double_spaced_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Use Separator Checkbox
        row += 1
        self.use_separator_var = tk.BooleanVar(value=False)
        separator_check = ttk.Checkbutton(
            main_frame,
            text="Use visual separator lines between prompts (recommended)",
            variable=self.use_separator_var
        )
        separator_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # API Key (masked entry)
        row += 1
        ttk.Label(main_frame, text="API Key:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value="")
        api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, show="*")
        api_key_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(Optional, for favorites)", foreground="gray").grid(
            row=row, column=2, sticky=tk.W, padx=(5, 0)
        )

        # Horizontal Separator Line
        row += 1
        h_separator = ttk.Separator(main_frame, orient="horizontal")
        h_separator.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Progress Bar
        row += 1
        ttk.Label(main_frame, text="Progress:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Log Output
        row += 1
        ttk.Label(main_frame, text="Log:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=5)
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=60,
            state="disabled",
            wrap=tk.WORD
        )
        self.log_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        main_frame.rowconfigure(row, weight=1)

        # Buttons
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start Scraping",
            command=self.start_scraping,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_scraping,
            state="disabled",
            width=20
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            width=20
        )
        clear_button.pack(side=tk.LEFT, padx=5)

    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)

    def log(self, message):
        """Add message to log."""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update()

    def clear_log(self):
        """Clear the log."""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")

    def start_scraping(self):
        """Start the scraping process."""
        if self.is_scraping:
            return

        # Validate inputs
        if not self.base_model_var.get():
            messagebox.showerror("Error", "Please select a base model")
            return

        # Update UI
        self.is_scraping = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_var.set("Scraping...")

        # Clear log
        self.clear_log()

        # Start scraping in a separate thread
        thread = threading.Thread(target=self.scrape_thread, daemon=True)
        thread.start()

    def stop_scraping(self):
        """Stop the scraping process."""
        self.is_scraping = False
        self.progress_var.set("Stopping...")
        self.log("Stopping scrape (will finish current model)...")

    def scrape_thread(self):
        """Thread function for scraping."""
        try:
            # Get parameters - "Any" means no filter (None)
            base_model_selection = self.base_model_var.get()
            base_model = None if base_model_selection == "Any" else base_model_selection
            model_type = self.model_type_var.get() if self.model_type_var.get() != "Any" else None
            max_images = self.max_images_var.get()
            sort = self.sort_var.get()
            period = self.period_var.get() if self.period_var.get() != "AllTime" else None
            nsfw = self.nsfw_var.get() if self.nsfw_var.get() != "Any" else None
            username = self.username_var.get().strip() if self.username_var.get().strip() else None
            delay = self.delay_var.get()
            output_dir = self.output_dir_var.get()
            export_prompts = self.export_prompts_var.get()
            double_spaced = self.double_spaced_var.get()
            use_separator = self.use_separator_var.get()
            api_key = self.api_key_var.get().strip() if self.api_key_var.get().strip() else None

            # Log configuration
            self.log(f"Configuration:")
            self.log(f"  Base Model: {base_model or 'Any'}")
            self.log(f"  Model Type: {model_type or 'Any'}")
            self.log(f"  Max Images: {max_images}")
            self.log(f"  Sort By: {sort}")
            self.log(f"  Period: {period or 'AllTime'}")
            self.log(f"  NSFW: {nsfw or 'Any'}")
            if username:
                self.log(f"  Username: {username}")
            self.log(f"  Delay: {delay}s")
            self.log(f"  Output Dir: {output_dir}")
            self.log(f"  Export Prompts: {export_prompts}")
            if export_prompts:
                self.log(f"  Double Spaced: {double_spaced}")
                self.log(f"  Use Separator: {use_separator}")
            if api_key:
                self.log(f"  API Key: ****{api_key[-4:]}")
            self.log("")

            # Initialize scraper with custom logging
            self.scraper = ScraperWithLogging(
                output_dir=output_dir,
                delay=delay,
                api_key=api_key,
                log_callback=self.log
            )

            # Scrape data - strict filtering only when specific base model selected
            if base_model:
                self.log(f"Strict filtering: Only images with base_model='{base_model}'")

            all_images = []
            page = 1
            images_per_page = min(200, max_images * 3)  # Fetch more to account for filtering
            pages_without_results = 0
            max_empty_pages = 5

            while len(all_images) < max_images and self.is_scraping:
                self.log(f"Fetching page {page}... (currently have {len(all_images)} images)")
                self.progress_var.set(f"Scraping: {len(all_images)}/{max_images} images...")

                images_data = self.scraper.get_images_by_filter(
                    base_model=base_model,
                    model_type=model_type,
                    limit=min(200, images_per_page),
                    page=page,
                    sort=sort,
                    period=period,
                    nsfw=nsfw,
                    username=username
                )

                items = images_data.get("items", [])
                if not items:
                    self.log("No more images found.")
                    break

                # Process each image - apply strict filtering only if base_model specified
                added_this_page = 0
                for image in items:
                    if len(all_images) >= max_images or not self.is_scraping:
                        break

                    processed_image = self.scraper.process_image_data(image)

                    # If base_model specified, filter strictly; otherwise accept all
                    if base_model is None or processed_image.get('base_model') == base_model:
                        all_images.append(processed_image)
                        added_this_page += 1

                if base_model:
                    self.log(f"  Matched {added_this_page} out of {len(items)} images")
                else:
                    self.log(f"  Added {added_this_page} images")

                if added_this_page == 0:
                    pages_without_results += 1
                else:
                    pages_without_results = 0

                # Stop if we've had too many pages without results
                if pages_without_results >= max_empty_pages:
                    self.log(f"No matching images found in {max_empty_pages} consecutive pages. Stopping.")
                    break

                page += 1

                if self.is_scraping:
                    import time
                    time.sleep(delay)

                # Check if we've reached the end
                metadata = images_data.get("metadata", {})
                if metadata.get("currentPage") >= metadata.get("totalPages", 1):
                    self.log("Reached last page.")
                    break

            if not self.is_scraping:
                self.log("\nScraping stopped by user")
            else:
                self.log(f"\nScraping completed!")

            # Save results if we got any
            if all_images:
                self.log(f"\nScraped {len(all_images)} images")
                self.log(f"Images with prompts: {sum(1 for r in all_images if r.get('prompt'))}")

                # Verify base models
                actual_base_models = set(img.get('base_model') for img in all_images)
                self.log(f"Base models in results: {actual_base_models}")

                self.log("\nSaving results...")
                self.scraper.save_results(all_images)

                if export_prompts:
                    self.log("Exporting prompts to text file...")
                    self.scraper.export_prompts_only(all_images, double_spaced=double_spaced,
                                                     use_separator=use_separator)

                self.log(f"\nResults saved to {output_dir}/")

                messagebox.showinfo(
                    "Success",
                    f"Scraped {len(all_images)} images\n"
                    f"Images with prompts: {sum(1 for r in all_images if r.get('prompt'))}\n"
                    f"Results saved to {output_dir}/"
                )
            else:
                self.log("\nNo images were scraped")
                messagebox.showwarning("Warning", "No images were scraped")

        except Exception as e:
            self.log(f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            # Reset UI
            self.is_scraping = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_var.set("Ready")


class ScraperWithLogging(CivitaiScraper):
    """Extended scraper with logging callback."""

    def __init__(self, output_dir="output", delay=1.0, api_key=None, log_callback=None):
        """Initialize with logging callback."""
        super().__init__(output_dir, delay, api_key)
        self.log_callback = log_callback

    def log(self, message):
        """Log message if callback is set."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = CivitaiScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
