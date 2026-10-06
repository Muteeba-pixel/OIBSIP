"""SecurePass — Password Security Workstation.

A professional, high-end desktop workstation for cryptographically secure
password generation and Information Theory entropy analysis.
"""

import sys
import tkinter as tk
from typing import Dict, List, Optional
import customtkinter as ctk

from securepass.core.evaluator import PasswordEvaluator
from securepass.core.generator import PasswordGenerator
from securepass.core.models import CompositionStats, HistoryEntry, PasswordPolicy, StrengthResult
from securepass.core.session import SessionHistory
from securepass.ui.clipboard import ClipboardManager
from securepass.ui.components import CompositionIndicator, SectionLabel, StatusMark, SubtleDivider
from securepass.ui.theme import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_TEXT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_ELEVATED,
    COLOR_SURFACE_HOVER,
    COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_WARNING,
    FONT_APP_SUBTITLE,
    FONT_APP_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HERO_PASSWORD,
    FONT_METRIC_NUM,
    FONT_METRIC_VALUE,
    FONT_PASSWORD_ROW,
    FONT_SECTION_LABEL,
    FONT_SMALL,
    FONT_SMALL_BOLD,
)


class SecurePassApp:
    """Master application controller for SecurePass Workstation."""

    def __init__(self, root: Optional[ctk.CTk] = None) -> None:
        self.root = root or ctk.CTk()
        self._configure_window()

        # Core Services
        self.generator = PasswordGenerator()
        self.session_history = SessionHistory(max_entries=5)

        # Reactive State
        self.current_password: str = ""
        self.current_strength: Optional[StrengthResult] = None
        self.is_masked: bool = False
        self._hero_copy_timer: Optional[str] = None
        self._row_timers: Dict[str, str] = {}
        self._row_mask_states: Dict[str, bool] = {}

        # Configuration Variables
        self.var_length = tk.IntVar(value=20)
        self.var_uppercase = tk.BooleanVar(value=True)
        self.var_lowercase = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=True)
        self.var_exclude_ambiguous = tk.BooleanVar(value=False)
        self.var_avoid_repeats = tk.BooleanVar(value=False)
        self.var_avoid_sequences = tk.BooleanVar(value=False)

        # Build Workstation UI
        self._build_header()
        self._build_workstation()
        self._bind_shortcuts()

        # Initial generation
        self.set_preset("STRONG")

    def _configure_window(self) -> None:
        """Configure desktop workstation window proportions and styling."""
        self.root.title("SecurePass — Password Security Workstation")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        win_w = 1100
        win_h = 780
        self.root.minsize(980, 680)

        # Center on screen
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        pos_x = max(0, (scr_w - win_w) // 2)
        pos_y = max(0, (scr_h - win_h) // 2 - 20)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    # =========================================================================
    # Header
    # =========================================================================

    def _build_header(self) -> None:
        """Build refined top branding and status bar."""
        header_bar = ctk.CTkFrame(
            self.root,
            height=52,
            corner_radius=0,
            fg_color=COLOR_SURFACE,
            border_color=COLOR_BORDER,
            border_width=1,
        )
        header_bar.pack(fill="x", side="top")
        header_bar.pack_propagate(False)

        # Left branding with security mark
        brand_frame = ctk.CTkFrame(header_bar, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=8)

        # Refined geometric security mark
        mark_label = ctk.CTkLabel(
            brand_frame,
            text="⬡",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_ACCENT,
            width=20,
        )
        mark_label.pack(side="left", padx=(0, 8))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="SECUREPASS",
            font=FONT_APP_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Password Security Workstation",
            font=FONT_APP_SUBTITLE,
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w")

        # Right status & theme controls
        controls_frame = ctk.CTkFrame(header_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=8)

        StatusMark(controls_frame).pack(side="left", padx=(0, 16))

        self.btn_theme = ctk.CTkButton(
            controls_frame,
            text="Light",
            font=FONT_SMALL,
            width=58,
            height=26,
            corner_radius=4,
            fg_color=COLOR_SURFACE_ELEVATED,
            hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_SECONDARY,
            command=self._toggle_theme,
        )
        self.btn_theme.pack(side="left")

    def _toggle_theme(self) -> None:
        """Switch appearance mode between Dark and Light."""
        current = ctk.get_appearance_mode()
        if current.lower() == "dark":
            ctk.set_appearance_mode("light")
            self.btn_theme.configure(text="Dark")
        else:
            ctk.set_appearance_mode("dark")
            self.btn_theme.configure(text="Light")

    # =========================================================================
    # Main Workstation Layout
    # =========================================================================

    def _build_workstation(self) -> None:
        """Construct the 2-pane primary workspace and bottom history section."""
        self.scroll = ctk.CTkScrollableFrame(self.root, fg_color=COLOR_BG)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(14, 16))

        # Upper Workspace (2-Column Grid)
        upper_grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        upper_grid.pack(fill="x", pady=(0, 10))
        upper_grid.grid_columnconfigure(0, weight=6, minsize=560)
        upper_grid.grid_columnconfigure(1, weight=4, minsize=360)

        # Left Column: Primary Generator Area
        col_left = ctk.CTkFrame(upper_grid, fg_color="transparent")
        col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        # Right Column: Supporting Analysis Area
        col_right = ctk.CTkFrame(upper_grid, fg_color="transparent")
        col_right.grid(row=0, column=1, sticky="nsew")

        # Build Sections
        self._build_hero_section(col_left)
        self._build_policy_section(col_left)
        self._build_advanced_security_section(col_left)

        self._build_analysis_section(col_right)

        # Bottom: Recent Session
        SubtleDivider(self.scroll, pady=12)
        self._build_session_history_section(self.scroll)

    # =========================================================================
    # Left Pane: 1. Hero Area (Generated Password)
    # =========================================================================

    def _build_hero_section(self, parent: ctk.CTkFrame) -> None:
        """Build the dominant hero password display and primary action button."""
        SectionLabel(parent, "GENERATED PASSWORD")

        # Hero Password Well
        self.hero_well = ctk.CTkFrame(
            parent,
            fg_color=COLOR_SURFACE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            height=66,
        )
        self.hero_well.pack(fill="x", pady=(0, 8))
        self.hero_well.pack_propagate(False)

        # Monospace display entry
        self.entry_password = ctk.CTkEntry(
            self.hero_well,
            font=FONT_HERO_PASSWORD,
            text_color=COLOR_TEXT_PRIMARY,
            fg_color="transparent",
            border_width=0,
            justify="left",
        )
        self.entry_password.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=8)

        # Integrated quick actions (Show/Hide & Copy)
        actions_box = ctk.CTkFrame(self.hero_well, fg_color="transparent")
        actions_box.pack(side="right", padx=(0, 10), pady=10)

        self.btn_toggle_mask = ctk.CTkButton(
            actions_box,
            text="◉ SHOW",
            font=FONT_SMALL_BOLD,
            width=68,
            height=30,
            corner_radius=4,
            fg_color=COLOR_SURFACE_ELEVATED,
            hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_SECONDARY,
            command=self._toggle_mask,
        )
        self.btn_toggle_mask.pack(side="left", padx=3)

        self.btn_copy = ctk.CTkButton(
            actions_box,
            text="COPY",
            font=FONT_SMALL_BOLD,
            width=64,
            height=30,
            corner_radius=4,
            fg_color=COLOR_SURFACE_ELEVATED,
            hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            command=self._copy_current_password,
        )
        self.btn_copy.pack(side="left", padx=3)

        # Hero Strength & Actions Row
        hero_meta = ctk.CTkFrame(parent, fg_color="transparent")
        hero_meta.pack(fill="x", pady=(0, 6))

        # Strength meter bar
        strength_bar_box = ctk.CTkFrame(hero_meta, fg_color="transparent")
        strength_bar_box.pack(fill="x", pady=(0, 8))

        self.lbl_hero_strength = ctk.CTkLabel(
            strength_bar_box,
            text="VERY STRONG",
            font=FONT_SMALL_BOLD,
            text_color=COLOR_SUCCESS,
            width=88,
            anchor="w",
        )
        self.lbl_hero_strength.pack(side="left")

        self.bar_hero_strength = ctk.CTkProgressBar(
            strength_bar_box,
            height=4,
            corner_radius=2,
            progress_color=COLOR_SUCCESS,
            fg_color=COLOR_SURFACE_SECONDARY,
        )
        self.bar_hero_strength.set(1.0)
        self.bar_hero_strength.pack(side="left", fill="x", expand=True, padx=(4, 12))

        self.lbl_hero_entropy = ctk.CTkLabel(
            strength_bar_box,
            text="~108 bits estimated entropy",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            anchor="e",
        )
        self.lbl_hero_entropy.pack(side="right")

        # Primary Generate Button Row
        gen_row = ctk.CTkFrame(parent, fg_color="transparent")
        gen_row.pack(fill="x", pady=(0, 12))

        self.btn_generate = ctk.CTkButton(
            gen_row,
            text="GENERATE PASSWORD",
            font=FONT_BODY_BOLD,
            height=38,
            width=210,
            corner_radius=4,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_ACCENT_TEXT,
            command=self.generate_password,
        )
        self.btn_generate.pack(side="left")

        ctk.CTkLabel(
            gen_row,
            text="Enter / Space to generate  •  Ctrl+C to copy",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            anchor="e",
        ).pack(side="right", pady=6)

    # =========================================================================
    # Left Pane: 2. Password Policy
    # =========================================================================

    def _build_policy_section(self, parent: ctk.CTkFrame) -> None:
        """Build the configuration policy area."""
        SubtleDivider(parent, pady=10)
        SectionLabel(parent, "PASSWORD POLICY")

        # Presets Row
        preset_row = ctk.CTkFrame(parent, fg_color="transparent")
        preset_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            preset_row,
            text="Presets",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            width=54,
            anchor="w",
        ).pack(side="left")

        self.seg_presets = ctk.CTkSegmentedButton(
            preset_row,
            values=["STANDARD", "STRONG", "MAXIMUM"],
            command=self.set_preset,
            font=FONT_SMALL_BOLD,
            height=26,
            corner_radius=4,
        )
        self.seg_presets.set("STRONG")
        self.seg_presets.pack(side="left", padx=(4, 0))

        # Length Header & Quick Chips
        len_header = ctk.CTkFrame(parent, fg_color="transparent")
        len_header.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            len_header,
            text="Length",
            font=FONT_BODY,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        ).pack(side="left")

        self.lbl_length_val = ctk.CTkLabel(
            len_header,
            text="20",
            font=FONT_BODY_BOLD,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="e",
        )
        self.lbl_length_val.pack(side="right")

        chips_box = ctk.CTkFrame(len_header, fg_color="transparent")
        chips_box.pack(side="right", padx=(0, 12))

        for p in (12, 16, 20, 32):
            ctk.CTkButton(
                chips_box,
                text=str(p),
                width=32,
                height=22,
                corner_radius=3,
                font=FONT_SMALL,
                fg_color=COLOR_SURFACE_ELEVATED,
                hover_color=COLOR_SURFACE_HOVER,
                text_color=COLOR_TEXT_SECONDARY,
                command=lambda val=p: self._set_length(val),
            ).pack(side="left", padx=1)

        # Smooth Length Slider
        self.slider_length = ctk.CTkSlider(
            parent,
            from_=8,
            to=64,
            number_of_steps=56,
            variable=self.var_length,
            command=self._on_slider_change,
            height=14,
            corner_radius=2,
            button_length=14,
            progress_color=COLOR_ACCENT,
        )
        self.slider_length.pack(fill="x", pady=(2, 10))

        # Character Types (2-Column Checkboxes)
        ctk.CTkLabel(
            parent,
            text="Character types",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))

        types_grid = ctk.CTkFrame(parent, fg_color="transparent")
        types_grid.pack(fill="x", pady=(0, 4))
        types_grid.grid_columnconfigure(0, weight=1)
        types_grid.grid_columnconfigure(1, weight=1)

        self.chk_upper = ctk.CTkCheckBox(
            types_grid,
            text="Uppercase (A-Z)",
            variable=self.var_uppercase,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_upper.grid(row=0, column=0, sticky="w", pady=3)

        self.chk_lower = ctk.CTkCheckBox(
            types_grid,
            text="Lowercase (a-z)",
            variable=self.var_lowercase,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_lower.grid(row=0, column=1, sticky="w", pady=3)

        self.chk_digits = ctk.CTkCheckBox(
            types_grid,
            text="Numbers (0-9)",
            variable=self.var_digits,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_digits.grid(row=1, column=0, sticky="w", pady=3)

        self.chk_symbols = ctk.CTkCheckBox(
            types_grid,
            text="Symbols (!@#$%^&*)",
            variable=self.var_symbols,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_symbols.grid(row=1, column=1, sticky="w", pady=3)

    # =========================================================================
    # Left Pane: 3. Advanced Security Options
    # =========================================================================

    def _build_advanced_security_section(self, parent: ctk.CTkFrame) -> None:
        """Build refined settings-style advanced security constraints."""
        SubtleDivider(parent, pady=10)
        SectionLabel(parent, "ADVANCED SECURITY")

        sec_box = ctk.CTkFrame(parent, fg_color="transparent")
        sec_box.pack(fill="x")

        self.chk_ambiguous = ctk.CTkCheckBox(
            sec_box,
            text="Exclude ambiguous characters (0, O, 1, l, I, |)",
            variable=self.var_exclude_ambiguous,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_ambiguous.pack(anchor="w", pady=3)

        self.chk_repeats = ctk.CTkCheckBox(
            sec_box,
            text="Avoid repeated characters",
            variable=self.var_avoid_repeats,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_repeats.pack(anchor="w", pady=3)

        self.chk_sequences = ctk.CTkCheckBox(
            sec_box,
            text="Avoid sequential patterns (e.g. abc, 123)",
            variable=self.var_avoid_sequences,
            font=FONT_BODY,
            corner_radius=3,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_policy_change,
        )
        self.chk_sequences.pack(anchor="w", pady=3)

        # Inline error message
        self.lbl_inline_error = ctk.CTkLabel(
            parent,
            text="At least one character type must be selected.",
            font=FONT_SMALL_BOLD,
            text_color=COLOR_DANGER,
            anchor="w",
        )

    # =========================================================================
    # Right Pane: Supporting Security Analysis Area
    # =========================================================================

    def _build_analysis_section(self, parent: ctk.CTkFrame) -> None:
        """Build the supporting security analysis panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLOR_SURFACE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
        )
        panel.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # 1. Strength Header & Specs
        SectionLabel(inner, "PASSWORD STRENGTH")

        self.lbl_side_strength = ctk.CTkLabel(
            inner,
            text="VERY STRONG",
            font=FONT_METRIC_VALUE,
            text_color=COLOR_SUCCESS,
            anchor="w",
        )
        self.lbl_side_strength.pack(anchor="w", pady=(0, 4))

        self.bar_side_strength = ctk.CTkProgressBar(
            inner,
            height=4,
            corner_radius=2,
            progress_color=COLOR_SUCCESS,
            fg_color=COLOR_SURFACE_SECONDARY,
        )
        self.bar_side_strength.set(1.0)
        self.bar_side_strength.pack(fill="x", pady=(0, 6))

        self.lbl_strength_desc = ctk.CTkLabel(
            inner,
            text="High brute-force margin & excellent diversity.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            anchor="w",
        )
        self.lbl_strength_desc.pack(anchor="w")

        # Metrics Breakdown
        SubtleDivider(inner, pady=10)

        metrics = [
            ("Entropy", self._make_metric_label(inner, "~108 bits")),
            ("Length", self._make_metric_label(inner, "20 chars")),
            ("Character diversity", self._make_metric_label(inner, "4 / 4")),
        ]
        self.lbl_entropy_metric = metrics[0][1]
        self.lbl_len_metric = metrics[1][1]
        self.lbl_div_metric = metrics[2][1]

        for label_text, widget in metrics:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=label_text,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w",
            ).pack(side="left")

            widget.pack(side="right")

        # 2. Character Mix
        SubtleDivider(inner, pady=10)
        SectionLabel(inner, "CHARACTER MIX")

        self.row_upper = CompositionIndicator(inner, "Uppercase", count=5, pct=0.35)
        self.row_lower = CompositionIndicator(inner, "Lowercase", count=7, pct=0.35)
        self.row_digits = CompositionIndicator(inner, "Numbers", count=4, pct=0.15)
        self.row_symbols = CompositionIndicator(inner, "Symbols", count=4, pct=0.15)

        # 3. Cryptographic Audit
        SubtleDivider(inner, pady=10)
        SectionLabel(inner, "CRYPTOGRAPHIC AUDIT")

        audit_items = [
            ("Entropy Source", "OS CSPRNG (secrets)"),
            ("Permutation", "Fisher-Yates Shuffle"),
            ("Memory Model", "RAM Volatile Only"),
            ("Specification", "NIST SP 800-63B"),
        ]

        for k, v in audit_items:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(
                row,
                text=k,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=v,
                font=FONT_SMALL_BOLD,
                text_color=COLOR_TEXT_PRIMARY,
                anchor="e",
            ).pack(side="right")

    def _make_metric_label(self, parent: ctk.CTkFrame, initial_text: str) -> ctk.CTkLabel:
        """Helper to create right-aligned metric value labels."""
        return ctk.CTkLabel(
            parent,
            text=initial_text,
            font=FONT_METRIC_NUM,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="e",
        )

    # =========================================================================
    # Bottom: Recent Session History
    # =========================================================================

    def _build_session_history_section(self, parent: ctk.CTkFrame) -> None:
        """Build the clean bottom session history section."""
        header_row = ctk.CTkFrame(parent, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            header_row,
            text="RECENT SESSION",
            font=FONT_SECTION_LABEL,
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(side="left")

        self.lbl_session_sub = ctk.CTkLabel(
            header_row,
            text="5 passwords",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_session_sub.pack(side="left", padx=12)

        self.btn_clear_session = ctk.CTkButton(
            header_row,
            text="Clear Session",
            font=FONT_SMALL,
            width=76,
            height=22,
            corner_radius=3,
            fg_color="transparent",
            hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_MUTED,
            command=self._clear_session_history,
        )
        self.btn_clear_session.pack(side="right")

        # History Rows Container
        self.history_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.history_container.pack(fill="x", pady=(0, 6))

        # Bottom Assurance Note
        ctk.CTkLabel(
            parent,
            text="Session-only. Passwords are not permanently stored. Generated locally using Python's secrets module.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        self._refresh_history_rows()

    # =========================================================================
    # Controller Logic & Actions
    # =========================================================================

    def set_preset(self, preset_name: str) -> None:
        """Apply predefined policy settings and regenerate password."""
        self.seg_presets.set(preset_name.upper())

        if preset_name.upper() == "STANDARD":
            self.var_length.set(14)
            self.var_uppercase.set(True)
            self.var_lowercase.set(True)
            self.var_digits.set(True)
            self.var_symbols.set(False)
            self.var_exclude_ambiguous.set(False)
            self.var_avoid_repeats.set(False)
            self.var_avoid_sequences.set(False)

        elif preset_name.upper() == "STRONG":
            self.var_length.set(20)
            self.var_uppercase.set(True)
            self.var_lowercase.set(True)
            self.var_digits.set(True)
            self.var_symbols.set(True)
            self.var_exclude_ambiguous.set(False)
            self.var_avoid_repeats.set(False)
            self.var_avoid_sequences.set(False)

        elif preset_name.upper() == "MAXIMUM":
            self.var_length.set(32)
            self.var_uppercase.set(True)
            self.var_lowercase.set(True)
            self.var_digits.set(True)
            self.var_symbols.set(True)
            self.var_exclude_ambiguous.set(True)
            self.var_avoid_repeats.set(True)
            self.var_avoid_sequences.set(True)

        self.lbl_length_val.configure(text=str(self.var_length.get()))
        self.slider_length.set(self.var_length.get())
        self.generate_password()

    def _set_length(self, val: int) -> None:
        """Set length via quick chip button."""
        self.var_length.set(val)
        self.lbl_length_val.configure(text=str(val))
        self.slider_length.set(val)
        self.generate_password()

    def _on_slider_change(self, val: float) -> None:
        """Callback when slider moves."""
        int_val = int(val)
        self.lbl_length_val.configure(text=str(int_val))
        self.generate_password()

    def _on_policy_change(self) -> None:
        """Callback when checkboxes change."""
        self.generate_password()

    def _get_active_policy(self) -> PasswordPolicy:
        """Construct PasswordPolicy instance from active UI state."""
        return PasswordPolicy(
            length=self.var_length.get(),
            include_uppercase=self.var_uppercase.get(),
            include_lowercase=self.var_lowercase.get(),
            include_digits=self.var_digits.get(),
            include_symbols=self.var_symbols.get(),
            exclude_ambiguous=self.var_exclude_ambiguous.get(),
            avoid_repeats=self.var_avoid_repeats.get(),
            avoid_sequences=self.var_avoid_sequences.get(),
        )

    def generate_password(self) -> None:
        """Generate password using CSPRNG secrets, evaluate strength, and update session."""
        policy = self._get_active_policy()

        # Check for zero enabled character sets
        if policy.active_sets_count() == 0:
            self.lbl_inline_error.pack(anchor="w", pady=(4, 0))
            self.btn_generate.configure(state="disabled")
            return
        else:
            self.lbl_inline_error.pack_forget()
            self.btn_generate.configure(state="normal")

        try:
            pwd = self.generator.generate(policy)
            self.current_password = pwd
            self.current_strength = PasswordEvaluator.evaluate(pwd)

            # Update password hero display
            self._update_hero_display()

            # Update strength displays (Hero & Side Analysis)
            self._update_strength_displays()

            # Update composition bars
            self._update_composition_display()

            # Add to volatile session history
            self.session_history.add(pwd, self.current_strength.label)
            self._refresh_history_rows()

        except ValueError as err:
            self.lbl_inline_error.configure(text=str(err))
            self.lbl_inline_error.pack(anchor="w", pady=(4, 0))

    def _update_hero_display(self) -> None:
        """Update password entry with plaintext or masked string."""
        self.entry_password.configure(state="normal")
        self.entry_password.delete(0, "end")

        if self.is_masked:
            self.entry_password.insert(0, "•" * len(self.current_password))
            self.btn_toggle_mask.configure(text="◉ SHOW")
        else:
            self.entry_password.insert(0, self.current_password)
            self.btn_toggle_mask.configure(text="◉ HIDE")

        self.entry_password.configure(state="readonly")

    def _toggle_mask(self) -> None:
        """Toggle between masked dots and plaintext password."""
        self.is_masked = not self.is_masked
        self._update_hero_display()

    def _copy_current_password(self) -> None:
        """Copy current password to clipboard with transient feedback."""
        if not self.current_password:
            return

        def _on_copied():
            self.btn_copy.configure(text="COPIED!", text_color=COLOR_SUCCESS)
            if self._hero_copy_timer:
                self.root.after_cancel(self._hero_copy_timer)
            self._hero_copy_timer = self.root.after(1800, self._reset_hero_copy_btn)

        ClipboardManager.copy_text(self.root, self.current_password, _on_copied)

    def _reset_hero_copy_btn(self) -> None:
        """Restore default copy button label."""
        self.btn_copy.configure(text="COPY", text_color=COLOR_TEXT_PRIMARY)
        self._hero_copy_timer = None

    def _update_strength_displays(self) -> None:
        """Refresh strength indicators in hero section and side analysis panel."""
        if not self.current_strength:
            return

        tier = self.current_strength.label
        color = self.current_strength.color_hex
        norm_score = self.current_strength.score / 4.0
        entropy = self.current_strength.entropy_bits
        length = len(self.current_password)

        # Update Hero Row
        self.lbl_hero_strength.configure(text=tier, text_color=color)
        self.bar_hero_strength.configure(progress_color=color)
        self.bar_hero_strength.set(norm_score)
        self.lbl_hero_entropy.configure(text=f"~{entropy} bits estimated entropy")

        # Update Side Panel
        self.lbl_side_strength.configure(text=tier, text_color=color)
        self.bar_side_strength.configure(progress_color=color)
        self.bar_side_strength.set(norm_score)
        self.lbl_strength_desc.configure(text=self.current_strength.feedback)

        self.lbl_entropy_metric.configure(text=f"~{entropy} bits")
        self.lbl_len_metric.configure(text=f"{length} chars")

        comp = self.current_strength.composition or CompositionStats(0, 0, 0, 0, length, 0)
        self.lbl_div_metric.configure(text=f"{comp.diversity_count} / 4")

    def _update_composition_display(self) -> None:
        """Update composition count and percentage progress bars."""
        if not self.current_strength or not self.current_strength.composition:
            return

        comp = self.current_strength.composition
        total = max(1, comp.total_length)

        self.row_upper.update_stat(comp.uppercase_count, comp.uppercase_count / total)
        self.row_lower.update_stat(comp.lowercase_count, comp.lowercase_count / total)
        self.row_digits.update_stat(comp.digits_count, comp.digits_count / total)
        self.row_symbols.update_stat(comp.symbols_count, comp.symbols_count / total)

    def _refresh_history_rows(self) -> None:
        """Re-render compact recent session rows."""
        for child in self.history_container.winfo_children():
            child.destroy()

        entries = self.session_history.get_entries()
        count = len(entries)
        self.lbl_session_sub.configure(text=f"{count} password{'s' if count != 1 else ''}")

        if not entries:
            ctk.CTkLabel(
                self.history_container,
                text="No passwords generated yet in this session.",
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
            ).pack(anchor="w", pady=2)
            self.btn_clear_session.configure(state="disabled")
            return

        self.btn_clear_session.configure(state="normal")

        for idx, entry in enumerate(entries, 1):
            row = ctk.CTkFrame(
                self.history_container,
                fg_color=COLOR_SURFACE,
                border_color=COLOR_BORDER_SUBTLE,
                border_width=1,
                corner_radius=4,
                height=32,
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # Index
            ctk.CTkLabel(
                row,
                text=f"{idx}.",
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                width=20,
            ).pack(side="left", padx=(8, 2))

            # Masked display
            is_revealed = not self._row_mask_states.get(entry.entry_id, True)
            display_str = entry.password if is_revealed else entry.masked_preview

            ctk.CTkLabel(
                row,
                text=display_str,
                font=FONT_PASSWORD_ROW,
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=4)

            # Length tag
            ctk.CTkLabel(
                row,
                text=f"{entry.length}c",
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                width=30,
            ).pack(side="left", padx=2)

            # Show/Hide
            ctk.CTkButton(
                row,
                text="HIDE" if is_revealed else "SHOW",
                width=46,
                height=22,
                corner_radius=3,
                font=FONT_SMALL,
                fg_color=COLOR_SURFACE_ELEVATED,
                hover_color=COLOR_SURFACE_HOVER,
                text_color=COLOR_TEXT_SECONDARY,
                command=lambda e=entry: self._toggle_history_row(e),
            ).pack(side="left", padx=2)

            # Copy button
            btn_copy = ctk.CTkButton(
                row,
                text="COPY",
                width=46,
                height=22,
                corner_radius=3,
                font=FONT_SMALL,
                fg_color=COLOR_SURFACE_ELEVATED,
                hover_color=COLOR_SURFACE_HOVER,
                text_color=COLOR_TEXT_PRIMARY,
            )
            btn_copy.configure(command=lambda e=entry, b=btn_copy: self._copy_history_entry(e, b))
            btn_copy.pack(side="right", padx=(2, 6))

    def _toggle_history_row(self, entry: HistoryEntry) -> None:
        """Toggle masked visibility for a single history item."""
        cur = self._row_mask_states.get(entry.entry_id, True)
        self._row_mask_states[entry.entry_id] = not cur
        self._refresh_history_rows()

    def _copy_history_entry(self, entry: HistoryEntry, btn: ctk.CTkButton) -> None:
        """Copy historical credential with inline feedback."""
        def _on_copied():
            btn.configure(text="COPIED!", text_color=COLOR_SUCCESS)
            entry_id = entry.entry_id
            if entry_id in self._row_timers:
                self.root.after_cancel(self._row_timers[entry_id])
            self._row_timers[entry_id] = self.root.after(
                1800, lambda: self._reset_history_copy_btn(btn, entry_id)
            )

        ClipboardManager.copy_text(self.root, entry.password, _on_copied)

    def _reset_history_copy_btn(self, btn: ctk.CTkButton, entry_id: str) -> None:
        """Restore history row copy button label."""
        try:
            btn.configure(text="COPY", text_color=COLOR_TEXT_PRIMARY)
        except Exception:
            pass
        self._row_timers.pop(entry_id, None)

    def _clear_session_history(self) -> None:
        """Purge volatile history buffer."""
        self.session_history.clear()
        self._row_mask_states.clear()
        self._refresh_history_rows()

    def _bind_shortcuts(self) -> None:
        """Register keyboard shortcuts."""
        self.root.bind("<Return>", lambda _e: self.generate_password())
        self.root.bind("<space>", lambda _e: self.generate_password())
        self.root.bind("<Control-c>", lambda _e: self._copy_current_password())
