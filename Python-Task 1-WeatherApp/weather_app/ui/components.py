"""Custom desktop UI components and autocomplete search widget for Atmos Weather Desk."""

import tkinter as tk
from typing import Callable, Optional, List
from .theme import Theme
from .icons import WeatherIconCanvas, SunArcCanvas
from ..core.models import ForecastDay, SunTimes, Location


class SurfaceCard(tk.Frame):
    """Refined container panel with a 1px border and designated elevation."""

    def __init__(
        self,
        master: tk.Widget,
        theme: Theme,
        bg: Optional[str] = None,
        border_color: Optional[str] = None,
        padding: int = 14,
        **kwargs
    ):
        self.theme = theme
        self.bg_color = bg or theme.colors.bg_surface
        self.border_color = border_color or theme.colors.border_card

        super().__init__(
            master,
            bg=self.bg_color,
            highlightbackground=self.border_color,
            highlightthickness=1,
            bd=0,
            padx=padding,
            pady=padding,
            **kwargs
        )

    def update_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.bg_color = theme.colors.bg_surface
        self.border_color = theme.colors.border_card
        self.configure(bg=self.bg_color, highlightbackground=self.border_color)


class MetricTile(SurfaceCard):
    """
    Compact, high-density meteorological metric tile.
    Presents category label, primary measurement value, and qualitative context note.
    """

    def __init__(
        self,
        master: tk.Widget,
        theme: Theme,
        label: str,
        initial_value: str = "--",
        initial_subtext: str = "--",
        **kwargs
    ):
        super().__init__(master, theme, padding=10, **kwargs)

        self.label_var = tk.StringVar(value=label.upper())
        self.value_var = tk.StringVar(value=initial_value)
        self.subtext_var = tk.StringVar(value=initial_subtext)

        # Header category
        self.lbl_category = tk.Label(
            self,
            textvariable=self.label_var,
            font=theme.font_badge(),
            fg=theme.colors.text_muted,
            bg=self.bg_color,
            anchor="w"
        )
        self.lbl_category.pack(fill=tk.X, anchor="w", pady=(0, 2))

        # Main Value
        self.lbl_value = tk.Label(
            self,
            textvariable=self.value_var,
            font=theme.font_metric_value(),
            fg=theme.colors.text_primary,
            bg=self.bg_color,
            anchor="w"
        )
        self.lbl_value.pack(fill=tk.X, anchor="w", pady=(0, 2))

        # Qualitative Note
        self.lbl_subtext = tk.Label(
            self,
            textvariable=self.subtext_var,
            font=theme.font_caption(),
            fg=theme.colors.text_secondary,
            bg=self.bg_color,
            anchor="w"
        )
        self.lbl_subtext.pack(fill=tk.X, anchor="w")

    def update_data(self, value: str, subtext: str) -> None:
        self.value_var.set(value)
        self.subtext_var.set(subtext)

    def update_theme(self, theme: Theme) -> None:
        super().update_theme(theme)
        self.lbl_category.configure(fg=theme.colors.text_muted, bg=self.bg_color)
        self.lbl_value.configure(fg=theme.colors.text_primary, bg=self.bg_color)
        self.lbl_subtext.configure(fg=theme.colors.text_secondary, bg=self.bg_color)


class ForecastDayCard(SurfaceCard):
    """Compact daily forecast block showing day, date, icon, condition, and min/max temperatures."""

    def __init__(self, master: tk.Widget, theme: Theme, **kwargs):
        super().__init__(master, theme, padding=10, **kwargs)

        self.day_var = tk.StringVar(value="--")
        self.date_var = tk.StringVar(value="--")
        self.cond_var = tk.StringVar(value="--")
        self.temp_var = tk.StringVar(value="-- / --")
        self.pop_var = tk.StringVar(value="")

        # Day Title (e.g. MON)
        self.lbl_day = tk.Label(
            self,
            textvariable=self.day_var,
            font=theme.font_body_bold(),
            fg=theme.colors.text_primary,
            bg=self.bg_color
        )
        self.lbl_day.pack(pady=(0, 1))

        # Date (e.g. Oct 6)
        self.lbl_date = tk.Label(
            self,
            textvariable=self.date_var,
            font=theme.font_badge(),
            fg=theme.colors.text_muted,
            bg=self.bg_color
        )
        self.lbl_date.pack(pady=(0, 4))

        # Weather glyph canvas
        self.icon_canvas = WeatherIconCanvas(
            self,
            condition="Clear",
            is_day=True,
            size=36,
            bg=self.bg_color
        )
        self.icon_canvas.pack(pady=(1, 4))

        # Condition summary
        self.lbl_cond = tk.Label(
            self,
            textvariable=self.cond_var,
            font=theme.font_caption(),
            fg=theme.colors.text_secondary,
            bg=self.bg_color
        )
        self.lbl_cond.pack(pady=(0, 3))

        # High / Low temperatures
        self.lbl_temp = tk.Label(
            self,
            textvariable=self.temp_var,
            font=theme.font_body_bold(),
            fg=theme.colors.text_primary,
            bg=self.bg_color
        )
        self.lbl_temp.pack(pady=(0, 2))

        # Rain Chance Pill
        self.lbl_pop = tk.Label(
            self,
            textvariable=self.pop_var,
            font=theme.font_badge(),
            fg=theme.colors.accent,
            bg=self.bg_color
        )
        self.lbl_pop.pack()

    def set_forecast(self, item: ForecastDay, is_day: bool = True) -> None:
        self.day_var.set(item.day_name.upper())
        self.date_var.set(item.date_str)
        self.cond_var.set(item.condition)
        self.temp_var.set(f"{round(item.temp_max)}°  {round(item.temp_min)}°")

        if item.pop > 10:
            self.pop_var.set(f"☂ {item.pop}%")
        else:
            self.pop_var.set("")

        self.icon_canvas.set_icon(item.condition, is_day=is_day, bg=self.bg_color)

    def update_theme(self, theme: Theme) -> None:
        super().update_theme(theme)
        self.lbl_day.configure(fg=theme.colors.text_primary, bg=self.bg_color)
        self.lbl_date.configure(fg=theme.colors.text_muted, bg=self.bg_color)
        self.lbl_cond.configure(fg=theme.colors.text_secondary, bg=self.bg_color)
        self.lbl_temp.configure(fg=theme.colors.text_primary, bg=self.bg_color)
        self.lbl_pop.configure(fg=theme.colors.accent, bg=self.bg_color)
        self.icon_canvas.set_canvas_bg(self.bg_color)


class SunArcWidget(SurfaceCard):
    """Dedicated Sun & Daylight section presenting the solar arc trajectory."""

    def __init__(self, master: tk.Widget, theme: Theme, **kwargs):
        super().__init__(master, theme, padding=12, **kwargs)

        self.lbl_title = tk.Label(
            self,
            text="SUN & DAYLIGHT CYCLE",
            font=theme.font_badge(),
            fg=theme.colors.text_muted,
            bg=self.bg_color,
            anchor="w"
        )
        self.lbl_title.pack(fill=tk.X, pady=(0, 4))

        self.arc_canvas = SunArcCanvas(
            self,
            width=280,
            height=85,
            bg=self.bg_color
        )
        self.arc_canvas.pack(fill=tk.X, expand=True)

    def update_sun(self, sun: SunTimes) -> None:
        self.arc_canvas.update_sun_cycle(
            sunrise_str=sun.sunrise_local,
            sunset_str=sun.sunset_local,
            daylight_str=sun.daylight_duration,
            progress=sun.solar_progress,
            is_day=sun.is_day,
            bg=self.bg_color
        )

    def update_theme(self, theme: Theme) -> None:
        super().update_theme(theme)
        self.lbl_title.configure(fg=theme.colors.text_muted, bg=self.bg_color)
        self.arc_canvas.set_canvas_bg(self.bg_color)


class AutocompleteDropdown(tk.Frame):
    """
    Custom-styled autocomplete suggestion menu.
    Renders cleanly directly below the search bar without default Tkinter listbox artifacts.
    """

    def __init__(
        self,
        master: tk.Widget,
        theme: Theme,
        on_select: Callable[[Location], None],
        **kwargs
    ):
        super().__init__(
            master,
            bg=theme.colors.bg_surface,
            highlightbackground=theme.colors.border_card,
            highlightthickness=1,
            bd=0,
            **kwargs
        )
        self.theme = theme
        self.on_select = on_select
        self.items: List[Location] = []
        self.selected_index: int = -1
        self.row_widgets: List[tk.Frame] = []

    def set_suggestions(self, locations: List[Location]) -> None:
        """Populate suggestion rows."""
        self.items = locations
        self.selected_index = -1

        for child in self.winfo_children():
            child.destroy()
        self.row_widgets.clear()

        if not locations:
            self.place_forget()
            return

        for idx, loc in enumerate(locations):
            row = tk.Frame(self, bg=self.theme.colors.bg_surface, cursor="hand2", padx=12, pady=6)
            row.pack(fill=tk.X)

            # Location icon
            lbl_icon = tk.Label(
                row,
                text="⚲",
                font=(self.theme.font_family, 10, "bold"),
                fg=self.theme.colors.accent,
                bg=self.theme.colors.bg_surface
            )
            lbl_icon.pack(side=tk.LEFT, padx=(0, 8))

            # Title & Subtitle group
            text_box = tk.Frame(row, bg=self.theme.colors.bg_surface)
            text_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

            lbl_name = tk.Label(
                text_box,
                text=loc.name,
                font=self.theme.font_body_bold(),
                fg=self.theme.colors.text_primary,
                bg=self.theme.colors.bg_surface,
                anchor="w"
            )
            lbl_name.pack(fill=tk.X, anchor="w")

            lbl_sub = tk.Label(
                text_box,
                text=loc.subtitle,
                font=self.theme.font_caption(),
                fg=self.theme.colors.text_muted,
                bg=self.theme.colors.bg_surface,
                anchor="w"
            )
            lbl_sub.pack(fill=tk.X, anchor="w")

            # Click and Hover bindings
            for w in (row, lbl_icon, text_box, lbl_name, lbl_sub):
                w.bind("<Button-1>", lambda e, l=loc: self.on_select(l))
                w.bind("<Enter>", lambda e, i=idx: self._highlight_index(i))

            self.row_widgets.append(row)

    def _highlight_index(self, index: int) -> None:
        """Update row background on keyboard or mouse hover."""
        self.selected_index = index
        for idx, row in enumerate(self.row_widgets):
            bg = self.theme.colors.bg_elevated if idx == index else self.theme.colors.bg_surface
            row.configure(bg=bg)
            for child in row.winfo_children():
                child.configure(bg=bg)
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        subchild.configure(bg=bg)

    def select_next(self) -> None:
        """Arrow down keyboard action."""
        if not self.items:
            return
        new_idx = (self.selected_index + 1) % len(self.items)
        self._highlight_index(new_idx)

    def select_prev(self) -> None:
        """Arrow up keyboard action."""
        if not self.items:
            return
        new_idx = (self.selected_index - 1) % len(self.items)
        self._highlight_index(new_idx)

    def get_selected_location(self) -> Optional[Location]:
        """Return the location currently selected via keyboard, or first item if none."""
        if not self.items:
            return None
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return self.items[0]

    def close(self) -> None:
        self.items.clear()
        self.selected_index = -1
        self.place_forget()


class SearchBar(tk.Frame):
    """
    Modern desktop search bar with autocomplete integration,
    keyboard navigation, and real-time suggestion retrieval.
    """

    def __init__(
        self,
        master: tk.Widget,
        theme: Theme,
        on_query_submit: Callable[[str], None],
        on_location_select: Callable[[Location], None],
        on_refresh: Callable[[], None],
        fetch_suggestions_fn: Callable[[str], List[Location]],
        show_refresh: bool = True,
        **kwargs
    ):
        super().__init__(master, bg=theme.colors.bg_app, **kwargs)
        self.theme = theme
        self.on_query_submit = on_query_submit
        self.on_location_select = on_location_select
        self.on_refresh = on_refresh
        self.fetch_suggestions_fn = fetch_suggestions_fn
        self.placeholder = "Search city or location..."
        self._debounce_after_id: Optional[str] = None

        # Input outer wrapper
        self.entry_frame = tk.Frame(
            self,
            bg=theme.colors.bg_input,
            highlightbackground=theme.colors.border_subtle,
            highlightcolor=theme.colors.border_focus,
            highlightthickness=1,
            bd=0
        )
        self.entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.search_icon_lbl = tk.Label(
            self.entry_frame,
            text="⌕",
            font=(theme.font_family, 12, "bold"),
            fg=theme.colors.text_muted,
            bg=theme.colors.bg_input
        )
        self.search_icon_lbl.pack(side=tk.LEFT, padx=(10, 4))

        self.entry = tk.Entry(
            self.entry_frame,
            font=theme.font_body(),
            fg=theme.colors.text_muted,
            bg=theme.colors.bg_input,
            insertbackground=theme.colors.text_primary,
            relief=tk.FLAT,
            bd=0
        )
        self.entry.insert(0, self.placeholder)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=7, padx=(0, 6))

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Down>", self._on_arrow_down)
        self.entry.bind("<Up>", self._on_arrow_up)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Escape>", lambda e: self.dropdown.close())

        # Search Button
        self.btn_search = tk.Button(
            self,
            text="Search",
            font=theme.font_body_bold(),
            fg=theme.colors.bg_app,
            bg=theme.colors.accent,
            activeforeground=theme.colors.bg_app,
            activebackground=theme.colors.accent_hover,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=18,
            pady=7,
            command=self._submit_text
        )
        self.btn_search.pack(side=tk.LEFT, padx=(0, 6))

        # Refresh Button (if enabled)
        self.btn_refresh = tk.Button(
            self,
            text="↻ Refresh",
            font=theme.font_body(),
            fg=theme.colors.text_primary,
            bg=theme.colors.bg_surface,
            activeforeground=theme.colors.text_primary,
            activebackground=theme.colors.bg_elevated,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=7,
            highlightbackground=theme.colors.border_subtle,
            highlightthickness=1,
            command=self.on_refresh
        )
        if show_refresh:
            self.btn_refresh.pack(side=tk.LEFT)

        # Autocomplete dropdown instance attached to parent
        self.dropdown = AutocompleteDropdown(
            self.winfo_toplevel(),
            theme=self.theme,
            on_select=self._handle_dropdown_select
        )

    def _on_focus_in(self, event=None) -> None:
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.theme.colors.text_primary)
        self.entry_frame.configure(highlightbackground=self.theme.colors.border_focus)

    def _on_focus_out(self, event=None) -> None:
        # Delayed close so clicks on dropdown row are registered
        self.after(200, self._check_close_dropdown)
        if not self.entry.get().strip():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.theme.colors.text_muted)
        self.entry_frame.configure(highlightbackground=self.theme.colors.border_subtle)

    def _check_close_dropdown(self) -> None:
        self.dropdown.close()

    def _on_key_release(self, event) -> None:
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return

        query = self.entry.get().strip()
        if not query or query == self.placeholder:
            self.dropdown.close()
            return

        if self._debounce_after_id:
            self.after_cancel(self._debounce_after_id)
        self._debounce_after_id = self.after(220, lambda: self._query_suggestions(query))

    def _query_suggestions(self, query: str) -> None:
        try:
            results = self.fetch_suggestions_fn(query)
            if results and self.entry.winfo_exists():
                self._show_dropdown(results)
            else:
                self.dropdown.close()
        except Exception:
            self.dropdown.close()

    def _show_dropdown(self, locations: List[Location]) -> None:
        self.dropdown.set_suggestions(locations)
        # Position dropdown directly below the search input
        x = self.entry_frame.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
        y = self.entry_frame.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.entry_frame.winfo_height() + 2
        width = self.entry_frame.winfo_width()
        self.dropdown.place(x=x, y=y, width=width)
        self.dropdown.lift()

    def _on_arrow_down(self, event) -> str:
        self.dropdown.select_next()
        return "break"

    def _on_arrow_up(self, event) -> str:
        self.dropdown.select_prev()
        return "break"

    def _on_enter(self, event) -> str:
        selected_loc = self.dropdown.get_selected_location()
        if selected_loc:
            self._handle_dropdown_select(selected_loc)
        else:
            self._submit_text()
        return "break"

    def _handle_dropdown_select(self, loc: Location) -> None:
        self.dropdown.close()
        self.set_query(loc.display_name)
        self.on_location_select(loc)

    def _submit_text(self) -> None:
        self.dropdown.close()
        query = self.entry.get().strip()
        if query and query != self.placeholder:
            self.on_query_submit(query)

    def set_query(self, text: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.configure(fg=self.theme.colors.text_primary)

    def get_query(self) -> str:
        text = self.entry.get().strip()
        return "" if text == self.placeholder else text

    def set_loading(self, is_loading: bool) -> None:
        state = tk.DISABLED if is_loading else tk.NORMAL
        self.btn_search.configure(state=state)
        self.btn_refresh.configure(state=state)
        self.entry.configure(state=state)

    def update_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.configure(bg=theme.colors.bg_app)
        self.entry_frame.configure(
            bg=theme.colors.bg_input,
            highlightbackground=theme.colors.border_subtle
        )
        self.search_icon_lbl.configure(
            fg=theme.colors.text_muted,
            bg=theme.colors.bg_input
        )
        self.entry.configure(
            bg=theme.colors.bg_input,
            insertbackground=theme.colors.text_primary
        )
        if self.entry.get() == self.placeholder:
            self.entry.configure(fg=theme.colors.text_muted)
        else:
            self.entry.configure(fg=theme.colors.text_primary)

        self.btn_search.configure(
            bg=theme.colors.accent,
            fg=theme.colors.bg_app,
            activebackground=theme.colors.accent_hover
        )
        self.btn_refresh.configure(
            bg=theme.colors.bg_surface,
            fg=theme.colors.text_primary,
            activebackground=theme.colors.bg_elevated,
            highlightbackground=theme.colors.border_subtle
        )


class RecentLocationsBar(tk.Frame):
    """Horizontal bar displaying clickable chip pills for recent locations."""

    def __init__(
        self,
        master: tk.Widget,
        theme: Theme,
        on_select: Callable[[Location], None],
        **kwargs
    ):
        super().__init__(master, bg=theme.colors.bg_app, **kwargs)
        self.theme = theme
        self.on_select = on_select
        self.chips_container = tk.Frame(self, bg=theme.colors.bg_app)
        self.chips_container.pack(fill=tk.X)

        self.lbl_recent = tk.Label(
            self.chips_container,
            text="Recent:",
            font=theme.font_caption_bold(),
            fg=theme.colors.text_muted,
            bg=theme.colors.bg_app
        )
        self.lbl_recent.pack(side=tk.LEFT, padx=(0, 6))

    def update_locations(self, locations: List[Location]) -> None:
        """Repaint recent location chips."""
        for child in self.chips_container.winfo_children():
            if child != self.lbl_recent:
                child.destroy()

        if not locations:
            self.lbl_recent.pack_forget()
            return

        self.lbl_recent.pack(side=tk.LEFT, padx=(0, 6))

        for loc in locations:
            btn = tk.Button(
                self.chips_container,
                text=loc.name,
                font=self.theme.font_caption(),
                fg=self.theme.colors.text_secondary,
                bg=self.theme.colors.badge_bg,
                activeforeground=self.theme.colors.text_primary,
                activebackground=self.theme.colors.bg_elevated,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=8,
                pady=2,
                command=lambda l=loc: self.on_select(l)
            )
            btn.pack(side=tk.LEFT, padx=3)

    def update_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.configure(bg=theme.colors.bg_app)
        self.chips_container.configure(bg=theme.colors.bg_app)
        self.lbl_recent.configure(fg=theme.colors.text_muted, bg=theme.colors.bg_app)
