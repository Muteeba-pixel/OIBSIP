"""Theme management, design tokens, and typography configuration."""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ThemeColors:
    """Palette color tokens for the interface."""
    bg_app: str            # Window background
    bg_surface: str        # Card / panel surface
    bg_elevated: str       # Hover state, inset panels
    bg_input: str          # Search entry background
    border_subtle: str     # 1px border lines
    border_card: str       # Card borders
    border_focus: str      # Focused inputs
    text_primary: str      # Main headings, values
    text_secondary: str    # Subtitles, labels
    text_muted: str        # Captions, inactive elements
    accent: str            # Primary action / brand tint
    accent_hover: str      # Button hover
    accent_subtle: str     # Chip background
    status_error: str      # Error indicators
    status_error_bg: str   # Error background
    status_success: str    # Online / fresh indicators
    badge_bg: str          # Tag pill backgrounds
    divider: str           # Subtle hairline dividers
    sun_gold: str          # Sun arc and solar elements
    moon_blue: str         # Moon and nocturnal elements


# Refined Day Palette: Deep graphite workstation with warm amber/gold daylight accents
DAY_COLORS = ThemeColors(
    bg_app="#0D1117",
    bg_surface="#161B22",
    bg_elevated="#1F2633",
    bg_input="#131720",
    border_subtle="#212836",
    border_card="#2A3447",
    border_focus="#F59E0B",
    text_primary="#F0F4F8",
    text_secondary="#94A3B8",
    text_muted="#64748B",
    accent="#F59E0B",
    accent_hover="#D97706",
    accent_subtle="#2E2312",
    status_error="#F87171",
    status_error_bg="#2D171A",
    status_success="#34D399",
    badge_bg="#1F2738",
    divider="#212836",
    sun_gold="#FBBF24",
    moon_blue="#818CF8"
)

# Refined Night Palette: Deep celestial graphite with indigo-lavender accents
NIGHT_COLORS = ThemeColors(
    bg_app="#0A0D13",
    bg_surface="#121620",
    bg_elevated="#1A212E",
    bg_input="#0F131C",
    border_subtle="#1E2535",
    border_card="#262F43",
    border_focus="#818CF8",
    text_primary="#EEF2F6",
    text_secondary="#8E9CB0",
    text_muted="#5B687D",
    accent="#818CF8",
    accent_hover="#6366F1",
    accent_subtle="#1F2338",
    status_error="#F87171",
    status_error_bg="#2D171A",
    status_success="#34D399",
    badge_bg="#1B2234",
    divider="#1E2535",
    sun_gold="#FBBF24",
    moon_blue="#A5B4FC"
)


class Theme:
    """Design system coordinator and Tkinter styling provider."""

    FONT_FAMILY = "Segoe UI"

    def __init__(self, is_day: bool = True):
        self.is_day = is_day
        self.colors = DAY_COLORS if is_day else NIGHT_COLORS
        self.font_family = self._resolve_font_family()

    def set_day_mode(self, is_day: bool) -> None:
        """Switch between daytime and nighttime visual variations."""
        self.is_day = is_day
        self.colors = DAY_COLORS if is_day else NIGHT_COLORS

    @classmethod
    def _resolve_font_family(cls) -> str:
        """Verify Segoe UI availability or fallback safely without creating extra Tk roots."""
        try:
            root = getattr(tk, "_default_root", None)
            if root is not None:
                available = root.tk.call("font", "families")
                if "Segoe UI" in available:
                    return "Segoe UI"
                if "Inter" in available:
                    return "Inter"
                if "Helvetica" in available:
                    return "Helvetica"
        except Exception:
            pass
        return "Segoe UI"

    # Typography scale
    def font_display(self) -> Tuple[str, int, str]:
        return (self.font_family, 52, "bold")

    def font_title_large(self) -> Tuple[str, int, str]:
        return (self.font_family, 22, "bold")

    def font_title(self) -> Tuple[str, int, str]:
        return (self.font_family, 16, "bold")

    def font_subtitle(self) -> Tuple[str, int, str]:
        return (self.font_family, 11, "normal")

    def font_section_title(self) -> Tuple[str, int, str]:
        return (self.font_family, 10, "bold")

    def font_metric_value(self) -> Tuple[str, int, str]:
        return (self.font_family, 14, "bold")

    def font_body_bold(self) -> Tuple[str, int, str]:
        return (self.font_family, 10, "bold")

    def font_body(self) -> Tuple[str, int, str]:
        return (self.font_family, 10, "normal")

    def font_caption(self) -> Tuple[str, int, str]:
        return (self.font_family, 9, "normal")

    def font_caption_bold(self) -> Tuple[str, int, str]:
        return (self.font_family, 9, "bold")

    def font_badge(self) -> Tuple[str, int, str]:
        return (self.font_family, 8, "bold")

    def apply_ttk_styles(self, root: tk.Tk) -> None:
        """Configure standard TTK styles to integrate cleanly with the custom palette."""
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=self.colors.bg_app)
        style.configure("Surface.TFrame", background=self.colors.bg_surface)
        style.configure("Elevated.TFrame", background=self.colors.bg_elevated)

        # Sleek vertical scrollbar style matching workstation aesthetic
        style.configure(
            "Dashboard.Vertical.TScrollbar",
            gripcount=0,
            background=self.colors.bg_surface,
            darkcolor=self.colors.bg_app,
            lightcolor=self.colors.bg_app,
            troughcolor=self.colors.bg_app,
            bordercolor=self.colors.border_subtle,
            arrowcolor=self.colors.text_muted,
            arrowsize=10,
            width=10,
        )
        style.map(
            "Dashboard.Vertical.TScrollbar",
            background=[
                ("active", self.colors.bg_elevated),
                ("pressed", self.colors.accent),
            ],
            arrowcolor=[
                ("active", self.colors.text_primary),
            ],
        )


_active_theme = Theme(is_day=True)


def get_theme() -> Theme:
    """Retrieve the global active Theme instance."""
    return _active_theme
