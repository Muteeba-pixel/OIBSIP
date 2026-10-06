"""SecurePass Workstation Design Tokens and Typography.

Sophisticated dark charcoal/graphite palette with warm gold/amber accent.
Inspired by professional developer tools and cybersecurity desktop utilities.
Supports dual-palette appearance switching via CustomTkinter color tuples.
"""

from typing import Tuple

# Surface & Canvas Architecture (Graphite / Charcoal base)
COLOR_BG: Tuple[str, str] = ("#F6F8FA", "#0D1117")
COLOR_SURFACE: Tuple[str, str] = ("#FFFFFF", "#161B22")
COLOR_SURFACE_SECONDARY: Tuple[str, str] = ("#F3F4F6", "#1C2128")
COLOR_SURFACE_ELEVATED: Tuple[str, str] = ("#E5E7EB", "#21262D")
COLOR_SURFACE_HOVER: Tuple[str, str] = ("#D0D7DE", "#282E36")

# Restrained Borders & Dividers
COLOR_BORDER: Tuple[str, str] = ("#D0D7DE", "#30363D")
COLOR_BORDER_SUBTLE: Tuple[str, str] = ("#E1E4E8", "#21262D")

# Distinctive Accent (Sophisticated warm gold/amber)
COLOR_ACCENT: Tuple[str, str] = ("#BF8700", "#D29922")
COLOR_ACCENT_HOVER: Tuple[str, str] = ("#9E6A03", "#E3B341")
COLOR_ACCENT_TEXT: Tuple[str, str] = ("#FFFFFF", "#0D1117")

# Aliases for backward compatibility
COLOR_PRIMARY = COLOR_ACCENT
COLOR_PRIMARY_HOVER = COLOR_ACCENT_HOVER
COLOR_SURFACE_ALT = COLOR_SURFACE_SECONDARY

# Semantic Status (Used strictly for genuine states, never decoration)
COLOR_SUCCESS: Tuple[str, str] = ("#1A7F37", "#3FB950")
COLOR_WARNING: Tuple[str, str] = ("#9E6A03", "#D29922")
COLOR_DANGER: Tuple[str, str] = ("#CF222E", "#F85149")

# Typography Colors
COLOR_TEXT_PRIMARY: Tuple[str, str] = ("#1F2328", "#F0F6FC")
COLOR_TEXT_SECONDARY: Tuple[str, str] = ("#656D76", "#8B949E")
COLOR_TEXT_MUTED: Tuple[str, str] = ("#8C959F", "#6E7681")

# Typography Hierarchy (Windows system fonts)
FONT_FAMILY: str = "Segoe UI"
FONT_MONO: str = "Consolas"

FONT_APP_TITLE = (FONT_FAMILY, 13, "bold")
FONT_APP_SUBTITLE = (FONT_FAMILY, 9, "normal")
FONT_SECTION_LABEL = (FONT_FAMILY, 9, "bold")
FONT_BODY = (FONT_FAMILY, 10, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "normal")
FONT_SMALL_BOLD = (FONT_FAMILY, 9, "bold")
FONT_TAG = (FONT_FAMILY, 8, "bold")

FONT_HERO_PASSWORD = (FONT_MONO, 18, "bold")
FONT_PASSWORD_ROW = (FONT_MONO, 10, "normal")
FONT_METRIC_VALUE = (FONT_FAMILY, 13, "bold")
FONT_METRIC_NUM = (FONT_MONO, 11, "bold")
