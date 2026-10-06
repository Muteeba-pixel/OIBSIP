"""Reusable UI widgets for SecurePass Workstation.

Lightweight desktop controls, thin dividers, and compact composition meters
designed for professional developer utilities.
"""

from typing import Callable, Optional, Tuple
import customtkinter as ctk

from securepass.ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE,
    COLOR_SUCCESS,
    COLOR_SURFACE_ELEVATED,
    COLOR_SURFACE_HOVER,
    COLOR_SURFACE_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_SECTION_LABEL,
    FONT_SMALL,
    FONT_SMALL_BOLD,
)


class SubtleDivider(ctk.CTkFrame):
    """A single-pixel horizontal divider line."""

    def __init__(self, parent: ctk.CTkBaseClass, pady: int = 12, **kwargs) -> None:
        super().__init__(
            parent,
            height=1,
            fg_color=COLOR_BORDER_SUBTLE,
            corner_radius=0,
            **kwargs
        )
        self.pack(fill="x", pady=pady)


class SectionLabel(ctk.CTkFrame):
    """An understated uppercase section label."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        text: str,
        right_widget: Optional[ctk.CTkBaseClass] = None,
        pady: Tuple[int, int] = (0, 6),
        **kwargs
    ) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.pack(fill="x", pady=pady)

        self.label = ctk.CTkLabel(
            self,
            text=text.upper(),
            font=FONT_SECTION_LABEL,
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.label.pack(side="left")

        if right_widget:
            right_widget.pack(side="right")


class CompositionIndicator(ctk.CTkFrame):
    """A thin, elegant composition meter row."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        label: str,
        count: int = 0,
        pct: float = 0.0,
        **kwargs
    ) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.pack(fill="x", pady=2)

        # Label (Left)
        self.lbl_name = ctk.CTkLabel(
            self,
            text=label,
            font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY,
            width=80,
            anchor="w",
        )
        self.lbl_name.pack(side="left")

        # Thin Meter Bar (Center, 4px height)
        self.bar = ctk.CTkProgressBar(
            self,
            height=4,
            corner_radius=2,
            progress_color=COLOR_ACCENT,
            fg_color=COLOR_SURFACE_SECONDARY,
        )
        self.bar.set(pct)
        self.bar.pack(side="left", fill="x", expand=True, padx=(4, 10))

        # Percentage & Count (Right)
        self.lbl_stat = ctk.CTkLabel(
            self,
            text=f"{int(pct * 100)}%",
            font=FONT_SMALL_BOLD,
            text_color=COLOR_TEXT_PRIMARY,
            width=40,
            anchor="e",
        )
        self.lbl_stat.pack(side="right")

    def update_stat(self, count: int, pct: float) -> None:
        """Update stat text and progress position."""
        self.lbl_stat.configure(text=f"{int(pct * 100)}%")
        self.bar.set(min(1.0, max(0.0, pct)))


class StatusMark(ctk.CTkFrame):
    """Refined header status pill."""

    def __init__(self, parent: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)

        dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 9),
            text_color=COLOR_SUCCESS,
            width=10,
        )
        dot.pack(side="left", padx=(0, 4))

        lbl = ctk.CTkLabel(
            self,
            text="Local • Secure",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
        )
        lbl.pack(side="left")
