#!/usr/bin/env python3
"""
Civitai Image Prompt Scraper GUI

Cross-platform GUI for scraping image prompts from Civitai.
Includes Image Scraper and Prompt Miner modes.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import threading
import json
import os
import time
from civitai_scraper import CivitaiScraper


# Path for user custom presets (sits next to the script, ignored by git)
CUSTOM_PRESETS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "custom_presets.json"
)


# ── Tooltip helper ────────────────────────────────────────────────────

class ToolTip:
    """Hover tooltip for any tkinter widget."""

    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._cancel)

    def _schedule(self, event=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)

    def _cancel(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", foreground="#333333",
            relief=tk.SOLID, borderwidth=1,
            font=("Segoe UI", 9), padx=6, pady=3, wraplength=350,
        )
        label.pack()

    def _hide(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


def tip(widget, text):
    """Shorthand to attach a tooltip."""
    ToolTip(widget, text)
    return widget


# ── Custom preset persistence ────────────────────────────────────────

def load_custom_presets():
    """Load user custom presets from JSON file."""
    if os.path.exists(CUSTOM_PRESETS_FILE):
        try:
            with open(CUSTOM_PRESETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_custom_presets_to_disk(presets):
    """Save user custom presets to JSON file."""
    with open(CUSTOM_PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2, ensure_ascii=False)


# ── Main GUI ──────────────────────────────────────────────────────────

class CivitaiScraperGUI:
    """GUI for Civitai scraper with tabbed interface."""

    BASE_MODELS = [
        "Any",
        # Popular / current
        "Flux.1 D", "Flux.1 S", "Flux.1 Krea", "Flux.1 Kontext",
        "Flux.2 D", "Flux.2 Klein 9B", "Flux.2 Klein 9B-base",
        "Flux.2 Klein 4B", "Flux.2 Klein 4B-base",
        "Illustrious", "NoobAI", "Pony", "Pony V7",
        "SDXL 1.0", "SD 1.5", "Chroma",
        # Other models
        "Anima", "AuraFlow", "CogVideoX", "HiDream",
        "Hunyuan 1", "Hunyuan Video", "Kling", "Kolors",
        "LTXV", "LTXV2", "Lumina", "Mochi", "Nano Banana",
        "OpenAI", "Other", "PixArt a", "PixArt E", "Qwen",
        "SD 1.4", "SD 2.0", "SD 2.1", "SD 3",
        "SD 1.5 LCM", "SD 1.5 Hyper",
        "SDXL Turbo", "SDXL Lightning", "SDXL Hyper",
        "Veo 3", "ZImageTurbo", "Z Image Base",
        # Video models
        "Wan Video 1.3B t2v", "Wan Video 14B t2v",
        "Wan Video 14B i2v 480p", "Wan Video 14B i2v 720p",
        "Wan Video 2.2 TI2V-5B", "Wan Video 2.2 I2V-A14B",
        "Wan Video 2.2 T2V-A14B", "Wan Video 2.5 T2V", "Wan Video 2.5 I2V",
    ]

    MODEL_TYPES = [
        "Any", "Checkpoint", "LORA", "LoCon", "TextualInversion",
        "Hypernetwork", "AestheticGradient", "Controlnet", "Poses",
    ]

    SORT_OPTIONS = ["Most Reactions", "Most Comments", "Newest"]
    PERIOD_OPTIONS = ["AllTime", "Year", "Month", "Week", "Day"]
    NSFW_OPTIONS = ["Any", "None", "Soft", "Mature", "X"]

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Civitai Image Prompt Scraper")
        self.root.geometry("780x720")
        self.root.minsize(650, 560)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # notebook
        self.root.rowconfigure(1, weight=0)  # shared output section
        self.root.rowconfigure(2, weight=1)  # bottom: log expands

        self.is_scraping = False
        self.scraper = None
        self.custom_presets = load_custom_presets()

        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets."""
        # ── Notebook (tabs) ──
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))

        scraper_tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(scraper_tab, text="  Image Scraper  ")
        self.create_scraper_tab(scraper_tab)

        miner_tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(miner_tab, text="  Prompt Miner  ")
        self.create_miner_tab(miner_tab)

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # ── Shared output section (between tabs and log) ──
        self._create_output_section(self.root, grid_row=1)

        # ── Bottom: progress + log + buttons ──
        bottom = ttk.Frame(self.root, padding=(6, 4, 6, 6))
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(1, weight=1)

        progress_frame = ttk.Frame(bottom)
        progress_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(
            side=tk.LEFT, padx=(4, 0))

        self.log_text = scrolledtext.ScrolledText(
            bottom, height=8, state="disabled", wrap=tk.WORD, font=("Consolas", 9)
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", pady=(4, 4))

        btn_frame = ttk.Frame(bottom)
        btn_frame.grid(row=2, column=0)

        self.start_button = ttk.Button(
            btn_frame, text="Start Scraping", command=self.start_operation, width=18
        )
        self.start_button.pack(side=tk.LEFT, padx=4)

        self.stop_button = ttk.Button(
            btn_frame, text="Stop", command=self.stop_scraping, state="disabled", width=18
        )
        self.stop_button.pack(side=tk.LEFT, padx=4)

        ttk.Button(
            btn_frame, text="Clear Log", command=self.clear_log, width=18
        ).pack(side=tk.LEFT, padx=4)

    # ── Shared output section ─────────────────────────────────────────

    def _create_output_section(self, parent, grid_row):
        """Create the shared Output LabelFrame (visible for both tabs)."""
        out = ttk.LabelFrame(parent, text="Output", padding=4)
        out.grid(row=grid_row, column=0, sticky="ew", padx=6, pady=(4, 0))
        out.columnconfigure(1, weight=1)

        # Dir + Browse
        ttk.Label(out, text="Directory:").grid(row=0, column=0, sticky="w", pady=2)
        self.output_dir_var = tk.StringVar(value="output")
        ttk.Entry(out, textvariable=self.output_dir_var).grid(
            row=0, column=1, sticky="ew", pady=2, padx=4)

        def _browse():
            d = filedialog.askdirectory(initialdir=self.output_dir_var.get())
            if d:
                self.output_dir_var.set(d)

        ttk.Button(out, text="Browse...", command=_browse).grid(
            row=0, column=2, padx=(0, 4), pady=2)

        # Format + API Key row
        fmt = ttk.Frame(out)
        fmt.grid(row=1, column=0, columnspan=3, sticky="ew", pady=2)

        self.save_json_var = tk.BooleanVar(value=True)
        tip(
            ttk.Checkbutton(fmt, text="Save JSON", variable=self.save_json_var),
            "Save full image metadata as a JSON file"
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.export_prompts_var = tk.BooleanVar(value=True)
        cb_text = ttk.Checkbutton(fmt, text="Save text prompts",
                                  variable=self.export_prompts_var)
        tip(cb_text, "Save prompts to a plain text file")
        cb_text.pack(side=tk.LEFT, padx=(0, 20))

        lbl_api = ttk.Label(fmt, text="API Key:")
        lbl_api.pack(side=tk.LEFT)
        tip(lbl_api, "Optional Civitai API key for accessing favorites "
                     "or restricted content")
        self.api_key_var = tk.StringVar(value="")
        ttk.Entry(fmt, textvariable=self.api_key_var, show="*", width=18).pack(
            side=tk.LEFT, padx=(4, 0))

        # Text sub-options row
        txt_opts = ttk.Frame(out)
        txt_opts.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 2))

        ttk.Label(txt_opts, text="Text options:", foreground="gray").pack(
            side=tk.LEFT, padx=(0, 6))

        self.one_per_line_var = tk.BooleanVar(value=True)
        cb_opl = tip(
            ttk.Checkbutton(txt_opts, text="One per line (cleaned)",
                            variable=self.one_per_line_var),
            "Clean each prompt (remove LoRA tags, weights, brackets)\n"
            "and write one per line for easy reuse"
        )
        cb_opl.pack(side=tk.LEFT, padx=(0, 8))

        self.positive_only_var = tk.BooleanVar(value=False)
        cb_pos = tip(
            ttk.Checkbutton(txt_opts, text="Positive only",
                            variable=self.positive_only_var),
            "Skip negative prompts in the text output"
        )
        cb_pos.pack(side=tk.LEFT, padx=(0, 8))

        self.use_separator_var = tk.BooleanVar(value=False)
        cb_sep = tip(
            ttk.Checkbutton(txt_opts, text="Separators",
                            variable=self.use_separator_var),
            "Add visual separator lines between prompts"
        )
        cb_sep.pack(side=tk.LEFT, padx=(0, 8))

        self.double_spaced_var = tk.BooleanVar(value=False)
        cb_dbl = tip(
            ttk.Checkbutton(txt_opts, text="Double spaced",
                            variable=self.double_spaced_var),
            "Add extra blank line between prompts"
        )
        cb_dbl.pack(side=tk.LEFT)

        # Wire toggle for text sub-options
        text_cbs = [cb_opl, cb_pos, cb_sep, cb_dbl]

        def _toggle():
            state = "normal" if self.export_prompts_var.get() else "disabled"
            for cb in text_cbs:
                cb.configure(state=state)

        cb_text.configure(command=_toggle)

    # ── Tab 1: Image Scraper ──────────────────────────────────────────

    def create_scraper_tab(self, parent):
        """Create compact Image Scraper controls."""
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
        r = 0

        # Row: Base Model + Model Type
        lbl = ttk.Label(parent, text="Base Model:")
        lbl.grid(row=r, column=0, sticky="w", pady=2)
        tip(lbl, "Filter by the base model architecture.\n"
                 "'Any' returns images from all models.")
        self.base_model_var = tk.StringVar(value="Any")
        ttk.Combobox(
            parent, textvariable=self.base_model_var,
            values=self.BASE_MODELS, state="readonly"
        ).grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 12))
        ttk.Label(parent, text="Type:").grid(row=r, column=2, sticky="w", pady=2)
        self.model_type_var = tk.StringVar(value="Any")
        tip(
            ttk.Combobox(parent, textvariable=self.model_type_var,
                         values=self.MODEL_TYPES, state="readonly"),
            "Filter by model type (Checkpoint, LoRA, etc.)"
        ).grid(row=r, column=3, sticky="ew", pady=2, padx=4)

        # Row: Max Images + Sort
        r += 1
        ttk.Label(parent, text="Max Images:").grid(
            row=r, column=0, sticky="w", pady=2)
        self.max_images_var = tk.IntVar(value=100)
        ttk.Spinbox(
            parent, from_=1, to=10000, textvariable=self.max_images_var, width=10
        ).grid(row=r, column=1, sticky="w", pady=2, padx=(4, 12))
        ttk.Label(parent, text="Sort:").grid(row=r, column=2, sticky="w", pady=2)
        self.sort_var = tk.StringVar(value="Most Reactions")
        tip(
            ttk.Combobox(parent, textvariable=self.sort_var,
                         values=self.SORT_OPTIONS, state="readonly"),
            "How to order the results"
        ).grid(row=r, column=3, sticky="ew", pady=2, padx=4)

        # Row: Period + NSFW
        r += 1
        lbl_per = ttk.Label(parent, text="Period:")
        lbl_per.grid(row=r, column=0, sticky="w", pady=2)
        tip(lbl_per, "Time window for the sort order.\n"
                     "The Civitai API does not support custom date ranges.")
        self.period_var = tk.StringVar(value="AllTime")
        ttk.Combobox(
            parent, textvariable=self.period_var,
            values=self.PERIOD_OPTIONS, state="readonly"
        ).grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 12))
        ttk.Label(parent, text="NSFW:").grid(row=r, column=2, sticky="w", pady=2)
        self.nsfw_var = tk.StringVar(value="Any")
        tip(
            ttk.Combobox(parent, textvariable=self.nsfw_var,
                         values=self.NSFW_OPTIONS, state="readonly"),
            "Content filter: 'None' = SFW only, 'Any' = no filter"
        ).grid(row=r, column=3, sticky="ew", pady=2, padx=4)

        # Row: Username + Delay
        r += 1
        ttk.Label(parent, text="Username:").grid(
            row=r, column=0, sticky="w", pady=2)
        self.username_var = tk.StringVar(value="")
        tip(
            ttk.Entry(parent, textvariable=self.username_var),
            "Optional: only scrape images from this Civitai user"
        ).grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 12))
        lbl_delay = ttk.Label(parent, text="Delay (s):")
        lbl_delay.grid(row=r, column=2, sticky="w", pady=2)
        tip(lbl_delay, "Seconds between API requests (rate limiting)")
        self.delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            parent, from_=0.1, to=10.0, increment=0.1,
            textvariable=self.delay_var, width=6
        ).grid(row=r, column=3, sticky="w", pady=2, padx=4)

    # ── Tab 2: Prompt Miner ───────────────────────────────────────────

    def create_miner_tab(self, parent):
        """Create compact Prompt Miner controls."""
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
        r = 0

        # Preset row with Save / Delete buttons
        ttk.Label(parent, text="Preset:").grid(row=r, column=0, sticky="w", pady=2)
        preset_frame = ttk.Frame(parent)
        preset_frame.grid(row=r, column=1, columnspan=3,
                          sticky="ew", pady=2, padx=4)
        preset_frame.columnconfigure(0, weight=1)

        self.mine_preset_var = tk.StringVar(value="Space / Sci-Fi")
        self.preset_combo = tip(
            ttk.Combobox(
                preset_frame, textvariable=self.mine_preset_var,
                values=self._get_all_preset_names(),
                state="readonly"
            ),
            "Choose a subject preset to auto-fill search terms,\n"
            "or select 'Custom' to enter your own"
        )
        self.preset_combo.grid(row=0, column=0, sticky="ew")
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

        tip(
            ttk.Button(preset_frame, text="Save...",
                       command=self._save_custom_preset, width=7),
            "Save current mining settings as a custom preset"
        ).grid(row=0, column=1, padx=(4, 0))

        tip(
            ttk.Button(preset_frame, text="Delete",
                       command=self._delete_custom_preset, width=7),
            "Delete the selected custom preset"
        ).grid(row=0, column=2, padx=(4, 0))

        # Search Terms
        r += 1
        lbl_search = ttk.Label(parent, text="Search:")
        lbl_search.grid(row=r, column=0, sticky="nw", pady=2)
        tip(lbl_search, "Comma-separated keywords to find in prompts.\n"
                        "Optional: word:2 for higher weight scoring.")
        self.mine_keywords_text = tk.Text(parent, height=2, wrap=tk.WORD)
        self.mine_keywords_text.grid(
            row=r, column=1, columnspan=3, sticky="ew", pady=2, padx=4)

        # Required + Extra Banned
        r += 1
        lbl_req = ttk.Label(parent, text="Required:")
        lbl_req.grid(row=r, column=0, sticky="w", pady=2)
        tip(lbl_req, "At least one of these words must appear.\n"
                     "Leave empty to use search terms as requirement.")
        self.mine_required_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.mine_required_var).grid(
            row=r, column=1, sticky="ew", pady=2, padx=(4, 12))
        lbl_ban = ttk.Label(parent, text="Banned:")
        lbl_ban.grid(row=r, column=2, sticky="w", pady=2)
        tip(lbl_ban, "Subject-specific words to reject.\n"
                     "Any match causes instant rejection.")
        self.mine_banned_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.mine_banned_var).grid(
            row=r, column=3, sticky="ew", pady=2, padx=4)

        # Filter checkboxes
        r += 1
        filt_row = ttk.Frame(parent)
        filt_row.grid(row=r, column=0, columnspan=4, sticky="ew", pady=2)

        self.mine_filter_characters_var = tk.BooleanVar(value=True)
        tip(
            ttk.Checkbutton(filt_row, text="Filter character tags",
                            variable=self.mine_filter_characters_var),
            "Reject prompts containing 1girl, 1boy, solo, etc."
        ).pack(side=tk.LEFT, padx=(0, 15))

        self.mine_filter_scoring_var = tk.BooleanVar(value=True)
        tip(
            ttk.Checkbutton(filt_row, text="Filter scoring tags",
                            variable=self.mine_filter_scoring_var),
            "Reject prompts containing score_, rating_ tags"
        ).pack(side=tk.LEFT)

        # Quality row
        r += 1
        q_frame = ttk.Frame(parent)
        q_frame.grid(row=r, column=0, columnspan=4, sticky="ew", pady=2)

        ttk.Label(q_frame, text="Min Length:").pack(side=tk.LEFT)
        self.mine_min_length_var = tk.IntVar(value=50)
        tip(
            ttk.Spinbox(q_frame, from_=0, to=1000,
                        textvariable=self.mine_min_length_var, width=5),
            "Minimum character length for a prompt to qualify"
        ).pack(side=tk.LEFT, padx=(2, 12))

        ttk.Label(q_frame, text="Max Commas:").pack(side=tk.LEFT)
        self.mine_max_commas_var = tk.IntVar(value=20)
        tip(
            ttk.Spinbox(q_frame, from_=1, to=100,
                        textvariable=self.mine_max_commas_var, width=5),
            "Reject tag-soup prompts with too many commas"
        ).pack(side=tk.LEFT, padx=(2, 12))

        ttk.Label(q_frame, text="Min Score:").pack(side=tk.LEFT)
        self.mine_min_score_var = tk.IntVar(value=1)
        tip(
            ttk.Spinbox(q_frame, from_=1, to=50,
                        textvariable=self.mine_min_score_var, width=5),
            "Minimum keyword match score.\n"
            "Each matching keyword adds its weight to the score."
        ).pack(side=tk.LEFT, padx=(2, 12))

        ttk.Label(q_frame, text="Target:").pack(side=tk.LEFT)
        self.mine_target_var = tk.IntVar(value=50)
        tip(
            ttk.Spinbox(q_frame, from_=1, to=1000,
                        textvariable=self.mine_target_var, width=5),
            "Stop after finding this many matching prompts"
        ).pack(side=tk.LEFT, padx=(2, 0))

        # Scan row: Sort / Period / NSFW / Base Model / Delay
        r += 1
        s_frame = ttk.Frame(parent)
        s_frame.grid(row=r, column=0, columnspan=4, sticky="ew", pady=2)

        ttk.Label(s_frame, text="Sort:").pack(side=tk.LEFT)
        self.mine_sort_var = tk.StringVar(value="Most Reactions")
        ttk.Combobox(
            s_frame, textvariable=self.mine_sort_var,
            values=self.SORT_OPTIONS, state="readonly", width=13
        ).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(s_frame, text="Period:").pack(side=tk.LEFT)
        self.mine_period_var = tk.StringVar(value="AllTime")
        ttk.Combobox(
            s_frame, textvariable=self.mine_period_var,
            values=self.PERIOD_OPTIONS, state="readonly", width=8
        ).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(s_frame, text="NSFW:").pack(side=tk.LEFT)
        self.mine_nsfw_var = tk.StringVar(value="Any")
        ttk.Combobox(
            s_frame, textvariable=self.mine_nsfw_var,
            values=self.NSFW_OPTIONS, state="readonly", width=7
        ).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(s_frame, text="Model:").pack(side=tk.LEFT)
        self.mine_base_model_var = tk.StringVar(value="Any")
        ttk.Combobox(
            s_frame, textvariable=self.mine_base_model_var,
            values=self.BASE_MODELS, state="readonly", width=13
        ).pack(side=tk.LEFT, padx=(2, 10))

        lbl_d = ttk.Label(s_frame, text="Delay:")
        lbl_d.pack(side=tk.LEFT)
        tip(lbl_d, "Seconds between API requests (rate limiting)")
        self.mine_delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            s_frame, from_=0.1, to=10.0, increment=0.1,
            textvariable=self.mine_delay_var, width=5
        ).pack(side=tk.LEFT, padx=(2, 0))

        # Load the default preset
        self._load_preset("Space / Sci-Fi")

    # ── Preset management ─────────────────────────────────────────────

    def _get_all_preset_names(self):
        """Return built-in preset names followed by custom preset names."""
        names = list(CivitaiScraper.MINING_PRESETS.keys())
        for name in sorted(self.custom_presets.keys()):
            if name not in names:
                names.append(name)
        return names

    def _refresh_preset_combo(self):
        """Refresh the preset combobox values."""
        self.preset_combo.configure(values=self._get_all_preset_names())

    def _save_custom_preset(self):
        """Save current mining settings as a custom preset."""
        name = simpledialog.askstring(
            "Save Preset",
            "Enter a name for this preset:",
            parent=self.root,
        )
        if not name or not name.strip():
            return
        name = name.strip()

        if name in CivitaiScraper.MINING_PRESETS:
            messagebox.showerror(
                "Error",
                f"'{name}' is a built-in preset and cannot be overwritten.")
            return

        # Capture current mining field state
        kw_text = self.mine_keywords_text.get("1.0", tk.END).strip()
        keywords = {}
        for pair in kw_text.replace("\n", ",").split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" in pair:
                word, weight = pair.rsplit(":", 1)
                try:
                    keywords[word.strip()] = int(weight.strip())
                except ValueError:
                    keywords[pair] = 1
            else:
                keywords[pair] = 1

        req_text = self.mine_required_var.get().strip()
        required = ([w.strip() for w in req_text.split(",") if w.strip()]
                    if req_text else [])
        ban_text = self.mine_banned_var.get().strip()
        banned = ([w.strip() for w in ban_text.split(",") if w.strip()]
                  if ban_text else [])

        preset = {
            "keywords": keywords,
            "required_words": required,
            "banned_words": banned,
            "min_length": self.mine_min_length_var.get(),
            "max_commas": self.mine_max_commas_var.get(),
            "min_score": self.mine_min_score_var.get(),
        }

        overwriting = name in self.custom_presets
        self.custom_presets[name] = preset
        save_custom_presets_to_disk(self.custom_presets)
        self._refresh_preset_combo()
        self.mine_preset_var.set(name)

        verb = "updated" if overwriting else "saved"
        messagebox.showinfo("Preset Saved", f"Preset '{name}' {verb}.")

    def _delete_custom_preset(self):
        """Delete the currently selected custom preset."""
        name = self.mine_preset_var.get()

        if name in CivitaiScraper.MINING_PRESETS:
            messagebox.showerror(
                "Error",
                f"'{name}' is a built-in preset and cannot be deleted.")
            return

        if name not in self.custom_presets:
            messagebox.showerror("Error", f"'{name}' is not a custom preset.")
            return

        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete custom preset '{name}'?"):
            return

        del self.custom_presets[name]
        save_custom_presets_to_disk(self.custom_presets)
        self._refresh_preset_combo()
        self.mine_preset_var.set("Custom")
        self._load_preset("Custom")

    # ── Event Handlers ────────────────────────────────────────────────

    def _on_tab_change(self, event):
        """Update start button text based on active tab."""
        if self.is_scraping:
            return
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0:
            self.start_button.configure(text="Start Scraping")
        else:
            self.start_button.configure(text="Start Mining")

    def _on_preset_change(self, event):
        """Load the selected preset into the mining fields."""
        self._load_preset(self.mine_preset_var.get())

    def _load_preset(self, preset_name):
        """Populate mining fields from a built-in or custom preset."""
        if preset_name in CivitaiScraper.MINING_PRESETS:
            preset = CivitaiScraper.MINING_PRESETS[preset_name]
        elif preset_name in self.custom_presets:
            preset = self.custom_presets[preset_name]
        else:
            return

        self.mine_keywords_text.delete("1.0", tk.END)
        if preset["keywords"]:
            parts = []
            for w, p in preset["keywords"].items():
                parts.append(f"{w}:{p}" if p != 1 else w)
            self.mine_keywords_text.insert("1.0", ", ".join(parts))

        self.mine_required_var.set(", ".join(preset["required_words"]))
        self.mine_banned_var.set(", ".join(preset["banned_words"]))
        self.mine_min_length_var.set(preset["min_length"])
        self.mine_max_commas_var.set(preset["max_commas"])
        self.mine_min_score_var.set(preset["min_score"])

    # ── Logging ───────────────────────────────────────────────────────

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

    # ── Operation Control ─────────────────────────────────────────────

    def start_operation(self):
        """Start the appropriate operation based on the active tab."""
        if self.is_scraping:
            return

        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0:
            self.start_scraping()
        else:
            self.start_mining()

    def stop_scraping(self):
        """Stop the current operation."""
        self.is_scraping = False
        self.progress_var.set("Stopping...")
        self.log("Stopping operation...")

    def _begin_operation(self):
        """Common setup before starting any operation."""
        self.is_scraping = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.clear_log()

    def _end_operation(self):
        """Common cleanup after any operation finishes."""
        self.is_scraping = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress_var.set("Ready")

    # ── Image Scraper ─────────────────────────────────────────────────

    def start_scraping(self):
        """Start the scraping process."""
        if not self.save_json_var.get() and not self.export_prompts_var.get():
            messagebox.showerror(
                "Error",
                "Please select at least one output format (JSON or Text)")
            return

        self._begin_operation()
        self.progress_var.set("Scraping...")
        threading.Thread(target=self.scrape_thread, daemon=True).start()

    def scrape_thread(self):
        """Thread function for scraping."""
        try:
            base_model_sel = self.base_model_var.get()
            base_model = None if base_model_sel == "Any" else base_model_sel
            model_type_sel = self.model_type_var.get()
            model_type = None if model_type_sel == "Any" else model_type_sel
            max_images = self.max_images_var.get()
            sort = self.sort_var.get()
            period_sel = self.period_var.get()
            period = None if period_sel == "AllTime" else period_sel
            nsfw_sel = self.nsfw_var.get()
            nsfw = None if nsfw_sel == "Any" else nsfw_sel
            username = self.username_var.get().strip() or None
            delay = self.delay_var.get()
            output_dir = self.output_dir_var.get()
            save_json = self.save_json_var.get()
            export_prompts = self.export_prompts_var.get()
            double_spaced = self.double_spaced_var.get()
            use_separator = self.use_separator_var.get()
            positive_only = self.positive_only_var.get()
            one_per_line = self.one_per_line_var.get()
            api_key = self.api_key_var.get().strip() or None

            self.log("Configuration:")
            self.log(f"  Base Model: {base_model or 'Any'}")
            self.log(f"  Model Type: {model_type or 'Any'}")
            self.log(f"  Max Images: {max_images}")
            self.log(f"  Sort: {sort}, Period: {period or 'AllTime'}, "
                     f"NSFW: {nsfw or 'Any'}")
            if username:
                self.log(f"  Username: {username}")
            self.log(f"  Delay: {delay}s, Output: {output_dir}")
            self.log(f"  Save JSON: {save_json}, Save Text: {export_prompts}")
            if export_prompts:
                opts = []
                if one_per_line:
                    opts.append("one-per-line")
                if positive_only:
                    opts.append("positive-only")
                if use_separator:
                    opts.append("separators")
                if double_spaced:
                    opts.append("double-spaced")
                self.log(f"  Text options: "
                         f"{', '.join(opts) if opts else 'default'}")
            if api_key:
                self.log(f"  API Key: ****{api_key[-4:]}")
            self.log("")

            self.scraper = ScraperWithLogging(
                output_dir=output_dir,
                delay=delay,
                api_key=api_key,
                log_callback=self.log
            )

            if base_model:
                self.log(f"Strict filtering: Only images with "
                         f"base_model='{base_model}'")

            all_images = []
            cursor = None
            pages_fetched = 0
            images_per_page = min(200, max_images * 3)
            pages_without_results = 0
            max_empty_pages = 5

            while len(all_images) < max_images and self.is_scraping:
                pages_fetched += 1
                self.log(f"Fetching page {pages_fetched}... "
                         f"({len(all_images)} images so far)")
                self.progress_var.set(
                    f"Scraping: {len(all_images)}/{max_images} images...")

                images_data = self.scraper.get_images_by_filter(
                    base_model=base_model,
                    model_type=model_type,
                    limit=min(200, images_per_page),
                    sort=sort,
                    period=period,
                    nsfw=nsfw,
                    username=username,
                    cursor=cursor,
                )

                items = images_data.get("items", [])
                if not items:
                    self.log("No more images found.")
                    break

                added_this_page = 0
                for image in items:
                    if len(all_images) >= max_images or not self.is_scraping:
                        break
                    processed = self.scraper.process_image_data(image)
                    if (base_model is None
                            or processed.get('base_model') == base_model):
                        all_images.append(processed)
                        added_this_page += 1

                if base_model:
                    self.log(f"  Matched {added_this_page}/{len(items)} images")
                else:
                    self.log(f"  Added {added_this_page} images")

                if added_this_page == 0:
                    pages_without_results += 1
                else:
                    pages_without_results = 0

                if pages_without_results >= max_empty_pages:
                    self.log(f"No matches in {max_empty_pages} consecutive "
                             f"pages. Stopping.")
                    break

                metadata = images_data.get("metadata", {})
                cursor = metadata.get("nextCursor")
                if not cursor:
                    self.log("Reached last page.")
                    break

                if self.is_scraping:
                    time.sleep(delay)

            if not self.is_scraping:
                self.log("\nScraping stopped by user")
            else:
                self.log("\nScraping completed!")

            if all_images:
                prompts_count = sum(
                    1 for r in all_images if r.get('prompt'))
                self.log(f"Scraped {len(all_images)} images "
                         f"({prompts_count} with prompts)")

                actual_models = set(
                    img.get('base_model') for img in all_images)
                self.log(f"Base models: {actual_models}")

                if save_json:
                    self.log("\nSaving JSON...")
                    self.scraper.save_results(all_images)

                if export_prompts:
                    self.log("Saving text prompts...")
                    self.scraper.export_prompts_only(
                        all_images,
                        double_spaced=double_spaced,
                        use_separator=use_separator,
                        positive_only=positive_only,
                        one_per_line=one_per_line,
                    )

                self.log(f"\nResults saved to {output_dir}/")

                saved_types = []
                if save_json:
                    saved_types.append("JSON")
                if export_prompts:
                    saved_types.append("Text")

                messagebox.showinfo(
                    "Success",
                    f"Scraped {len(all_images)} images\n"
                    f"Images with prompts: {prompts_count}\n"
                    f"Saved: {' + '.join(saved_types)}\n"
                    f"Output: {output_dir}/"
                )
            else:
                self.log("\nNo images were scraped")
                messagebox.showwarning("Warning", "No images were scraped")

        except Exception as e:
            self.log(f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self._end_operation()

    # ── Prompt Miner ──────────────────────────────────────────────────

    def start_mining(self):
        """Start the prompt mining process."""
        kw_text = self.mine_keywords_text.get("1.0", tk.END).strip()
        if not kw_text:
            messagebox.showerror(
                "Error", "Please enter keywords or select a preset")
            return

        if not self.save_json_var.get() and not self.export_prompts_var.get():
            messagebox.showerror(
                "Error",
                "Please select at least one output format (JSON or Text)")
            return

        keywords = {}
        for pair in kw_text.replace("\n", ",").split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" in pair:
                word, weight = pair.rsplit(":", 1)
                try:
                    keywords[word.strip()] = int(weight.strip())
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Invalid weight in keyword: '{pair}'\n"
                        f"Expected format: word:number"
                    )
                    return
            else:
                keywords[pair] = 1

        if not keywords:
            messagebox.showerror("Error", "No valid keywords found")
            return

        self._begin_operation()
        self.progress_var.set("Mining...")
        threading.Thread(
            target=self.mine_thread, args=(keywords,), daemon=True
        ).start()

    def mine_thread(self, keywords):
        """Thread function for prompt mining."""
        try:
            preset_name = self.mine_preset_var.get()
            required_text = self.mine_required_var.get().strip()
            required_words = (
                [w.strip() for w in required_text.split(",") if w.strip()]
                if required_text else [])

            banned_words = []
            if self.mine_filter_characters_var.get():
                banned_words.extend(CivitaiScraper.BANNED_CHARACTER_TAGS)
            if self.mine_filter_scoring_var.get():
                banned_words.extend(CivitaiScraper.BANNED_SCORING_TAGS)
            banned_text = self.mine_banned_var.get().strip()
            if banned_text:
                banned_words.extend(
                    w.strip() for w in banned_text.split(",") if w.strip())

            min_length = self.mine_min_length_var.get()
            max_commas = self.mine_max_commas_var.get()
            min_score = self.mine_min_score_var.get()
            target_count = self.mine_target_var.get()
            sort = self.mine_sort_var.get()
            period_sel = self.mine_period_var.get()
            period = None if period_sel == "AllTime" else period_sel
            nsfw_sel = self.mine_nsfw_var.get()
            nsfw = None if nsfw_sel == "Any" else nsfw_sel
            model_sel = self.mine_base_model_var.get()
            base_model = None if model_sel == "Any" else model_sel
            delay = self.mine_delay_var.get()
            output_dir = self.output_dir_var.get()
            api_key = self.api_key_var.get().strip() or None
            save_json = self.save_json_var.get()
            save_text = self.export_prompts_var.get()
            use_separator = self.use_separator_var.get()
            one_per_line = self.one_per_line_var.get()

            # Use preset name as filename prefix (skip for "Custom")
            file_prefix = preset_name if preset_name != "Custom" else None

            self.log("Prompt Mining Configuration:")
            self.log(f"  Preset: {preset_name}")
            self.log(f"  Search terms: {len(keywords)}, "
                     f"Required: {len(required_words)}, "
                     f"Banned: {len(banned_words)}")
            self.log(f"  Quality: min_len={min_length}, "
                     f"max_commas={max_commas}, min_score={min_score}")
            self.log(f"  Target: {target_count}, Sort: {sort}, "
                     f"Period: {period or 'AllTime'}, "
                     f"NSFW: {nsfw or 'Any'}")
            if base_model:
                self.log(f"  Base Model: {base_model}")
            self.log(f"  Delay: {delay}s, Output: {output_dir}")
            self.log(f"  Format: JSON={save_json}, Text={save_text}"
                     f"{' (one per line)' if one_per_line and save_text else ''}")
            if api_key:
                self.log(f"  API Key: ****{api_key[-4:]}")
            self.log("")

            scraper = ScraperWithLogging(
                output_dir=output_dir,
                delay=delay,
                api_key=api_key,
                log_callback=self.log
            )

            def mining_log(msg):
                self.log(msg)
                if msg.startswith("[MATCH #"):
                    try:
                        count = int(msg.split("#")[1].split("]")[0])
                        self.progress_var.set(
                            f"Mining: {count}/{target_count} matches...")
                    except (IndexError, ValueError):
                        pass

            results = scraper.mine_prompts(
                keywords=keywords,
                required_words=required_words,
                banned_words=banned_words,
                min_length=min_length,
                max_commas=max_commas,
                min_score=min_score,
                target_count=target_count,
                sort=sort,
                period=period,
                nsfw=nsfw,
                base_model=base_model,
                is_running_callback=lambda: self.is_scraping,
                log_callback=mining_log,
            )

            if not self.is_scraping:
                self.log("\nMining stopped by user")

            if results:
                self.log(f"\nMining complete! Found {len(results)} "
                         f"matching prompts.")
                self.log(f"Score range: {results[-1][1]} to {results[0][1]}")
                self.log("\nExporting results...")

                if save_json:
                    scraper.save_mined_json(
                        results, filename_prefix=file_prefix)

                if save_text:
                    scraper.export_mined_prompts(
                        results,
                        use_separator=use_separator,
                        one_per_line=one_per_line,
                        filename_prefix=file_prefix,
                    )

                self.log(f"Results saved to {output_dir}/")

                saved_types = []
                if save_json:
                    saved_types.append("JSON")
                if save_text:
                    saved_types.append("Text")

                messagebox.showinfo(
                    "Success",
                    f"Found {len(results)} matching prompts\n"
                    f"Score range: {results[-1][1]} - {results[0][1]}\n"
                    f"Saved: {' + '.join(saved_types)}\n"
                    f"Output: {output_dir}/"
                )
            else:
                self.log("\nNo matching prompts found")
                messagebox.showwarning("Warning", "No matching prompts found")

        except Exception as e:
            self.log(f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self._end_operation()


class ScraperWithLogging(CivitaiScraper):
    """Extended scraper with logging callback."""

    def __init__(self, output_dir="output", delay=1.0, api_key=None,
                 log_callback=None):
        super().__init__(output_dir, delay, api_key)
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)


def main():
    """Run the GUI application."""
    root = tk.Tk()
    CivitaiScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
