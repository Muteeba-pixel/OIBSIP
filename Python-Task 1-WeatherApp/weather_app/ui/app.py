"""Main desktop application window for Atmos Weather Desk."""

import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional, List

from .theme import Theme, get_theme
from .icons import WeatherIconCanvas
from .components import (
    SurfaceCard,
    MetricTile,
    ForecastDayCard,
    SunArcWidget,
    SearchBar,
    RecentLocationsBar,
)
from ..core.api import (
    WeatherAPIError,
    CityNotFoundError,
    AuthenticationError,
    MissingApiKeyError,
    InvalidApiKeyError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
)
from ..core.weather_service import WeatherService
from ..core.models import Location, WeatherData


POPULAR_LOCATIONS = [
    Location("Lahore", 31.5204, 74.3587, "PK", "Punjab"),
    Location("Islamabad", 33.6844, 73.0479, "PK", "Islamabad Capital Territory"),
    Location("Karachi", 24.8607, 67.0011, "PK", "Sindh"),
    Location("Tokyo", 35.6762, 139.6503, "JP", "Tokyo"),
    Location("London", 51.5074, -0.1278, "GB", "England"),
    Location("New York", 40.7128, -74.0060, "US", "New York"),
    Location("Dubai", 25.2048, 55.2708, "AE", "Dubai"),
    Location("Paris", 48.8566, 2.3522, "FR", "Île-de-France"),
]


class WeatherApp:
    """Primary desktop GUI application controller."""

    TARGET_WIDTH = 1140
    TARGET_HEIGHT = 740
    MIN_WIDTH = 980
    MIN_HEIGHT = 520

    def __init__(self, root: tk.Tk, service: Optional[WeatherService] = None):
        self.root = root
        self.theme = get_theme()
        self.service = service or WeatherService()

        # Session memory for recent searches (max 5 Location objects)
        self.recent_locations: List[Location] = []
        self.current_location: Optional[Location] = None
        self.current_data: Optional[WeatherData] = None
        self._is_fetching = False

        self._init_window()
        self._build_header_branding()
        self._build_view_containers()
        self._bind_shortcuts()
        self.show_welcome_view()

    @property
    def current_city(self) -> Optional[str]:
        """Convenience property returning currently active city name."""
        return self.current_location.name if self.current_location else None

    def _detect_work_area(self) -> Tuple[int, int]:
        """
        Detect usable desktop screen / work-area dimensions (excluding taskbar on Windows).
        Falls back safely across platforms.
        """
        try:
            import ctypes
            from ctypes import wintypes
            class RECT(ctypes.Structure):
                _fields_ = [
                    ('left', wintypes.LONG),
                    ('top', wintypes.LONG),
                    ('right', wintypes.LONG),
                    ('bottom', wintypes.LONG)
                ]
            rect = RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                w = int(rect.right - rect.left)
                h = int(rect.bottom - rect.top)
                if w > 0 and h > 0:
                    return w, h
        except Exception:
            pass

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        return sw, max(420, sh - 70)

    def _init_window(self) -> None:
        """Configure root window geometry dynamically based on available screen space."""
        self.root.title("Atmos — Weather Desk")

        work_w, work_h = self._detect_work_area()

        # Window chrome & title bar allowance on Windows
        avail_h = max(520, work_h - 40)
        avail_w = max(980, work_w - 40)

        # Set sensible target dimensions that do not exceed available height
        win_w = min(self.TARGET_WIDTH, avail_w)
        win_h = min(self.TARGET_HEIGHT, avail_h)

        # Center window within the work area
        pos_x = max(0, (work_w - win_w) // 2)
        pos_y = max(0, (work_h - win_h) // 2)

        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        # Sensible minsize adapted to screen
        min_w = min(self.MIN_WIDTH, max(800, work_w - 60))
        min_h = min(self.MIN_HEIGHT, max(480, work_h - 80))
        self.root.minsize(min_w, min_h)

        self.root.configure(bg=self.theme.colors.bg_app)
        self.theme.apply_ttk_styles(self.root)

    # -------------------------------------------------------------
    # Header Branding & Global Strip
    # -------------------------------------------------------------

    def _build_header_branding(self) -> None:
        """Top bar with brand identity, active search strip, and status indicators."""
        self.header_frame = tk.Frame(self.root, bg=self.theme.colors.bg_app, padx=24, pady=12)
        self.header_frame.pack(fill=tk.X)

        # Top row: Brand & Status Pills
        top_row = tk.Frame(self.header_frame, bg=self.theme.colors.bg_app)
        top_row.pack(fill=tk.X, pady=(0, 8))

        # Brand Identity (Left)
        brand_box = tk.Frame(top_row, bg=self.theme.colors.bg_app)
        brand_box.pack(side=tk.LEFT)

        self.btn_logo = tk.Button(
            brand_box,
            text=" ATMOS ",
            font=self.theme.font_badge(),
            fg=self.theme.colors.bg_app,
            bg=self.theme.colors.accent,
            activeforeground=self.theme.colors.bg_app,
            activebackground=self.theme.colors.accent_hover,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            pady=2,
            command=self.show_welcome_view
        )
        self.btn_logo.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(brand_box, bg=self.theme.colors.bg_app)
        title_box.pack(side=tk.LEFT)

        self.lbl_app_title = tk.Label(
            title_box,
            text="Weather Desk",
            font=self.theme.font_title(),
            fg=self.theme.colors.text_primary,
            bg=self.theme.colors.bg_app
        )
        self.lbl_app_title.pack(anchor="w")

        self.lbl_app_subtitle = tk.Label(
            title_box,
            text="Live weather intelligence for your day",
            font=self.theme.font_caption(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app
        )
        self.lbl_app_subtitle.pack(anchor="w")

        # Right Status / Navigation
        status_box = tk.Frame(top_row, bg=self.theme.colors.bg_app)
        status_box.pack(side=tk.RIGHT)

        self.btn_home = tk.Button(
            status_box,
            text="Search Location",
            font=self.theme.font_caption_bold(),
            fg=self.theme.colors.text_secondary,
            bg=self.theme.colors.bg_surface,
            activeforeground=self.theme.colors.text_primary,
            activebackground=self.theme.colors.bg_elevated,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=3,
            highlightbackground=self.theme.colors.border_subtle,
            highlightthickness=1,
            command=self.show_welcome_view
        )
        self.btn_home.pack(side=tk.RIGHT, padx=(8, 0))

        self.day_night_pill = tk.Label(
            status_box,
            text="● STATION READY",
            font=self.theme.font_badge(),
            fg=self.theme.colors.accent,
            bg=self.theme.colors.badge_bg,
            padx=8,
            pady=4
        )
        self.day_night_pill.pack(side=tk.RIGHT, padx=(8, 0))

        self.timestamp_lbl = tk.Label(
            status_box,
            text="OpenWeatherMap API",
            font=self.theme.font_caption(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app
        )
        self.timestamp_lbl.pack(side=tk.RIGHT)

        # Dashboard Search Bar Strip (Visible in Dashboard view)
        self.dashboard_search_frame = tk.Frame(self.header_frame, bg=self.theme.colors.bg_app)

        self.dashboard_search_bar = SearchBar(
            self.dashboard_search_frame,
            self.theme,
            on_query_submit=self._handle_text_query_submit,
            on_location_select=self._handle_location_select,
            on_refresh=self.refresh_weather,
            fetch_suggestions_fn=self.service.search_locations,
            show_refresh=True
        )
        self.dashboard_search_bar.pack(fill=tk.X, pady=(0, 4))

        self.recent_chips = RecentLocationsBar(
            self.dashboard_search_frame,
            self.theme,
            on_select=self._handle_location_select
        )
        self.recent_chips.pack(fill=tk.X)

    # -------------------------------------------------------------
    # View Containers (Welcome, Loading, Dashboard, Error)
    # -------------------------------------------------------------

    def _build_view_containers(self) -> None:
        """Create main view holder frames."""
        self.viewport = tk.Frame(self.root, bg=self.theme.colors.bg_app, padx=24, pady=8)
        self.viewport.pack(fill=tk.BOTH, expand=True)

        self._build_welcome_view()
        self._build_loading_view()
        self._build_dashboard_view()
        self._build_error_view()
        self._build_bottom_bar()

    # -------------------------------------------------------------
    # 1. Welcome View (Intentional Initial State)
    # -------------------------------------------------------------

    def _build_welcome_view(self) -> None:
        """Construct the polished welcome / launch view."""
        self.welcome_frame = tk.Frame(self.viewport, bg=self.theme.colors.bg_app)

        center_box = tk.Frame(self.welcome_frame, bg=self.theme.colors.bg_app)
        center_box.pack(expand=True, pady=30)

        # Welcome Icon Glyph
        self.welcome_icon = WeatherIconCanvas(
            center_box,
            condition="Clear",
            is_day=True,
            size=64,
            bg=self.theme.colors.bg_app
        )
        self.welcome_icon.pack(pady=(0, 12))

        # Title
        lbl_welcome_title = tk.Label(
            center_box,
            text="Atmos Weather Desk",
            font=self.theme.font_title_large(),
            fg=self.theme.colors.text_primary,
            bg=self.theme.colors.bg_app
        )
        lbl_welcome_title.pack(pady=(0, 6))

        # Subtitle
        lbl_welcome_sub = tk.Label(
            center_box,
            text="Live weather intelligence for your day. Search for any city or location worldwide.",
            font=self.theme.font_subtitle(),
            fg=self.theme.colors.text_secondary,
            bg=self.theme.colors.bg_app
        )
        lbl_welcome_sub.pack(pady=(0, 24))

        # Search Box Container
        search_wrapper = tk.Frame(center_box, bg=self.theme.colors.bg_app, width=540)
        search_wrapper.pack(pady=(0, 16))

        self.welcome_search_bar = SearchBar(
            search_wrapper,
            self.theme,
            on_query_submit=self._handle_text_query_submit,
            on_location_select=self._handle_location_select,
            on_refresh=self.refresh_weather,
            fetch_suggestions_fn=self.service.search_locations,
            show_refresh=False
        )
        self.welcome_search_bar.pack(fill=tk.X)

        # Popular Locations Row
        popular_box = tk.Frame(center_box, bg=self.theme.colors.bg_app)
        popular_box.pack(pady=(0, 20))

        lbl_popular = tk.Label(
            popular_box,
            text="Popular locations:",
            font=self.theme.font_caption_bold(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app
        )
        lbl_popular.pack(side=tk.LEFT, padx=(0, 8))

        for loc in POPULAR_LOCATIONS:
            btn = tk.Button(
                popular_box,
                text=loc.name,
                font=self.theme.font_caption(),
                fg=self.theme.colors.text_secondary,
                bg=self.theme.colors.badge_bg,
                activeforeground=self.theme.colors.text_primary,
                activebackground=self.theme.colors.bg_elevated,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=9,
                pady=3,
                command=lambda l=loc: self._handle_location_select(l)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # Recent Locations Row on Welcome View (if any)
        self.welcome_recent_chips = RecentLocationsBar(
            center_box,
            self.theme,
            on_select=self._handle_location_select
        )
        self.welcome_recent_chips.pack(pady=(4, 0))

    # -------------------------------------------------------------
    # 2. Loading View
    # -------------------------------------------------------------

    def _build_loading_view(self) -> None:
        """Construct the non-blocking loading view."""
        self.loading_frame = tk.Frame(self.viewport, bg=self.theme.colors.bg_app)
        center_box = tk.Frame(self.loading_frame, bg=self.theme.colors.bg_app)
        center_box.pack(expand=True)

        self.loading_icon = WeatherIconCanvas(
            center_box,
            condition="Clear",
            is_day=True,
            size=52,
            bg=self.theme.colors.bg_app
        )
        self.loading_icon.pack(pady=(0, 16))

        self.lbl_loading_city = tk.Label(
            center_box,
            text="Loading weather...",
            font=self.theme.font_title(),
            fg=self.theme.colors.text_primary,
            bg=self.theme.colors.bg_app
        )
        self.lbl_loading_city.pack(pady=(0, 6))

        self.lbl_loading_sub = tk.Label(
            center_box,
            text="Querying OpenWeatherMap metric station...",
            font=self.theme.font_caption(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app
        )
        self.lbl_loading_sub.pack()

    # -------------------------------------------------------------
    # 3. Dashboard View (Active Workstation)
    # -------------------------------------------------------------

    def _build_dashboard_view(self) -> None:
        """Construct the complete multi-panel weather dashboard with responsive vertical scrolling."""
        self.dashboard_frame = tk.Frame(self.viewport, bg=self.theme.colors.bg_app)

        # Scrollable canvas for the dashboard content
        self.dashboard_canvas = tk.Canvas(
            self.dashboard_frame,
            bg=self.theme.colors.bg_app,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.dashboard_scrollbar = ttk.Scrollbar(
            self.dashboard_frame,
            orient=tk.VERTICAL,
            command=self.dashboard_canvas.yview,
            style="Dashboard.Vertical.TScrollbar"
        )
        self.dashboard_canvas.configure(yscrollcommand=self.dashboard_scrollbar.set)
        self.dashboard_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner Content Frame holding the panels
        self.dashboard_content = tk.Frame(self.dashboard_canvas, bg=self.theme.colors.bg_app)
        self.dashboard_canvas_window = self.dashboard_canvas.create_window(
            (0, 0),
            window=self.dashboard_content,
            anchor="nw"
        )

        self.dashboard_content.columnconfigure(0, weight=4, minsize=380)
        self.dashboard_content.columnconfigure(1, weight=6, minsize=620)
        self.dashboard_content.rowconfigure(0, weight=1)

        # Left Column: Station Overview & Hero Condition
        self._build_left_hero_panel(self.dashboard_content)

        # Right Column: Atmospheric Conditions, Sun Arc, and Forecast
        self._build_right_intelligence_panel(self.dashboard_content)

        # Dynamic layout bindings
        self.dashboard_canvas.bind("<Configure>", self._on_dashboard_canvas_configure)
        self.dashboard_content.bind("<Configure>", self._on_dashboard_content_configure)

    def _on_dashboard_canvas_configure(self, event) -> None:
        """Keep inner content frame width in sync with canvas width."""
        self.dashboard_canvas.itemconfig(self.dashboard_canvas_window, width=event.width)
        self._update_dashboard_scroll()

    def _on_dashboard_content_configure(self, event=None) -> None:
        """Update canvas scroll region and toggle scrollbar visibility when content size changes."""
        self._update_dashboard_scroll()

    def _update_dashboard_scroll(self) -> None:
        """Recalculate scrollregion and show/hide vertical scrollbar as needed."""
        self.dashboard_canvas.update_idletasks()
        bbox = self.dashboard_canvas.bbox("all")
        if bbox:
            self.dashboard_canvas.configure(scrollregion=bbox)
        content_h = self.dashboard_content.winfo_reqheight()
        canvas_h = self.dashboard_canvas.winfo_height()
        if canvas_h > 1 and content_h > canvas_h:
            if not self.dashboard_scrollbar.winfo_ismapped():
                self.dashboard_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        else:
            if self.dashboard_scrollbar.winfo_ismapped():
                self.dashboard_scrollbar.pack_forget()

    def _build_left_hero_panel(self, parent: tk.Widget) -> None:
        """Left Column: Weather Station Primary Hero Card."""
        self.left_hero_card = SurfaceCard(parent, self.theme, padding=20)
        self.left_hero_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # City Name
        self.lbl_city_title = tk.Label(
            self.left_hero_card,
            text="--",
            font=self.theme.font_title_large(),
            fg=self.theme.colors.text_primary,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_city_title.pack(fill=tk.X, pady=(0, 2))

        # Subtitle: Region and Country
        self.lbl_region_country = tk.Label(
            self.left_hero_card,
            text="--",
            font=self.theme.font_body(),
            fg=self.theme.colors.text_secondary,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_region_country.pack(fill=tk.X, pady=(0, 4))

        # Local Date and Time
        self.lbl_local_datetime = tk.Label(
            self.left_hero_card,
            text="--",
            font=self.theme.font_caption(),
            fg=self.theme.colors.text_muted,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_local_datetime.pack(fill=tk.X, pady=(0, 14))

        # Hero Weather Display (Icon + Big Temp + Condition)
        hero_box = tk.Frame(self.left_hero_card, bg=self.left_hero_card.bg_color)
        hero_box.pack(fill=tk.X, pady=(4, 14))

        self.hero_icon = WeatherIconCanvas(
            hero_box,
            condition="Clear",
            is_day=True,
            size=76,
            bg=self.left_hero_card.bg_color
        )
        self.hero_icon.pack(side=tk.LEFT, padx=(0, 16))

        temp_group = tk.Frame(hero_box, bg=self.left_hero_card.bg_color)
        temp_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lbl_hero_temp = tk.Label(
            temp_group,
            text="--°C",
            font=self.theme.font_display(),
            fg=self.theme.colors.text_primary,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_hero_temp.pack(anchor="w")

        self.lbl_hero_cond = tk.Label(
            temp_group,
            text="--",
            font=self.theme.font_subtitle(),
            fg=self.theme.colors.text_secondary,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_hero_cond.pack(anchor="w")

        # Feels like & High / Low
        self.lbl_feels_like = tk.Label(
            self.left_hero_card,
            text="--",
            font=self.theme.font_body(),
            fg=self.theme.colors.accent,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_feels_like.pack(fill=tk.X, pady=(0, 4))

        self.lbl_high_low = tk.Label(
            self.left_hero_card,
            text="--",
            font=self.theme.font_body_bold(),
            fg=self.theme.colors.text_secondary,
            bg=self.left_hero_card.bg_color,
            anchor="w"
        )
        self.lbl_high_low.pack(fill=tk.X, pady=(0, 14))

        # Hairline separator
        sep = tk.Frame(self.left_hero_card, height=1, bg=self.theme.colors.border_subtle)
        sep.pack(fill=tk.X, pady=(0, 14))

        # Station Overview Quick Glance Grid
        glance_box = tk.Frame(self.left_hero_card, bg=self.left_hero_card.bg_color)
        glance_box.pack(fill=tk.BOTH, expand=True)
        glance_box.columnconfigure(0, weight=1)
        glance_box.columnconfigure(1, weight=1)

        self.glance_humidity = self._create_glance_item(glance_box, 0, 0, "HUMIDITY", "--")
        self.glance_wind = self._create_glance_item(glance_box, 0, 1, "WIND", "--")
        self.glance_visibility = self._create_glance_item(glance_box, 1, 0, "VISIBILITY", "--")
        self.glance_pressure = self._create_glance_item(glance_box, 1, 1, "PRESSURE", "--")

    def _create_glance_item(
        self, parent: tk.Widget, row: int, col: int, label: str, value: str
    ) -> tk.StringVar:
        frame = tk.Frame(parent, bg=self.left_hero_card.bg_color, padx=4, pady=6)
        frame.grid(row=row, column=col, sticky="w", padx=4, pady=4)

        lbl = tk.Label(
            frame,
            text=label,
            font=self.theme.font_badge(),
            fg=self.theme.colors.text_muted,
            bg=self.left_hero_card.bg_color
        )
        lbl.pack(anchor="w")

        var = tk.StringVar(value=value)
        val_lbl = tk.Label(
            frame,
            textvariable=var,
            font=self.theme.font_body_bold(),
            fg=self.theme.colors.text_primary,
            bg=self.left_hero_card.bg_color
        )
        val_lbl.pack(anchor="w")
        return var

    def _build_right_intelligence_panel(self, parent: tk.Widget) -> None:
        """Right Column: Atmospheric Conditions, Sun Arc, and Forecast."""
        right_panel = tk.Frame(parent, bg=self.theme.colors.bg_app)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        # 1. Atmospheric Metrics Grid
        lbl_sec1 = tk.Label(
            right_panel,
            text="ATMOSPHERIC CONDITIONS",
            font=self.theme.font_section_title(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app,
            anchor="w"
        )
        lbl_sec1.pack(fill=tk.X, pady=(0, 6))

        metrics_grid = tk.Frame(right_panel, bg=self.theme.colors.bg_app)
        metrics_grid.pack(fill=tk.X, pady=(0, 10))
        for col in range(3):
            metrics_grid.columnconfigure(col, weight=1)

        self.tile_wind = MetricTile(metrics_grid, self.theme, "Wind Velocity", "--", "--")
        self.tile_wind.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        self.tile_humidity = MetricTile(metrics_grid, self.theme, "Humidity", "--", "--")
        self.tile_humidity.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        self.tile_pressure = MetricTile(metrics_grid, self.theme, "Pressure", "--", "--")
        self.tile_pressure.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)

        self.tile_visibility = MetricTile(metrics_grid, self.theme, "Visibility", "--", "--")
        self.tile_visibility.grid(row=1, column=0, sticky="nsew", padx=3, pady=3)

        self.tile_clouds = MetricTile(metrics_grid, self.theme, "Cloud Coverage", "--", "--")
        self.tile_clouds.grid(row=1, column=1, sticky="nsew", padx=3, pady=3)

        self.tile_dew = MetricTile(metrics_grid, self.theme, "Dew Point", "--", "--")
        self.tile_dew.grid(row=1, column=2, sticky="nsew", padx=3, pady=3)

        # 2. Sun & Daylight Cycle Widget
        self.sun_arc_widget = SunArcWidget(right_panel, self.theme)
        self.sun_arc_widget.pack(fill=tk.X, pady=(0, 10))

        # 3. 5-Day Forecast Strip
        lbl_sec2 = tk.Label(
            right_panel,
            text="5-DAY EXTENDED FORECAST",
            font=self.theme.font_section_title(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app,
            anchor="w"
        )
        lbl_sec2.pack(fill=tk.X, pady=(0, 6))

        self.forecast_strip = tk.Frame(right_panel, bg=self.theme.colors.bg_app)
        self.forecast_strip.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        for col in range(5):
            self.forecast_strip.columnconfigure(col, weight=1)

        self.forecast_cards: List[ForecastDayCard] = []
        for i in range(5):
            card = ForecastDayCard(self.forecast_strip, self.theme)
            card.grid(row=0, column=i, sticky="nsew", padx=3, pady=0)
            self.forecast_cards.append(card)

    # -------------------------------------------------------------
    # 4. Error View
    # -------------------------------------------------------------

    def _build_error_view(self) -> None:
        """Construct the dedicated error view."""
        self.error_frame = tk.Frame(self.viewport, bg=self.theme.colors.bg_app)
        center_box = SurfaceCard(self.error_frame, self.theme, padding=28)
        center_box.pack(expand=True, pady=40)

        # Warning icon
        lbl_err_icon = tk.Label(
            center_box,
            text="⚠",
            font=(self.theme.font_family, 26, "bold"),
            fg=self.theme.colors.status_error,
            bg=center_box.bg_color
        )
        lbl_err_icon.pack(pady=(0, 8))

        # Title
        self.lbl_error_title = tk.Label(
            center_box,
            text="Unable to load weather",
            font=self.theme.font_title(),
            fg=self.theme.colors.text_primary,
            bg=center_box.bg_color
        )
        self.lbl_error_title.pack(pady=(0, 6))

        # Message description
        self.lbl_error_desc = tk.Label(
            center_box,
            text="An unexpected issue occurred while fetching meteorological data.",
            font=self.theme.font_subtitle(),
            fg=self.theme.colors.text_secondary,
            bg=center_box.bg_color,
            wraplength=460,
            justify=tk.CENTER
        )
        self.lbl_error_desc.pack(pady=(0, 16))

        # Actions
        btn_box = tk.Frame(center_box, bg=center_box.bg_color)
        btn_box.pack()

        self.btn_err_retry = tk.Button(
            btn_box,
            text="Retry",
            font=self.theme.font_body_bold(),
            fg=self.theme.colors.bg_app,
            bg=self.theme.colors.accent,
            activeforeground=self.theme.colors.bg_app,
            activebackground=self.theme.colors.accent_hover,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=16,
            pady=6,
            command=self.refresh_weather
        )
        self.btn_err_retry.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_err_home = tk.Button(
            btn_box,
            text="Search Another Location",
            font=self.theme.font_body(),
            fg=self.theme.colors.text_primary,
            bg=self.theme.colors.bg_elevated,
            activeforeground=self.theme.colors.text_primary,
            activebackground=self.theme.colors.bg_surface,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=6,
            command=self.show_welcome_view
        )
        self.btn_err_home.pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # Bottom Status Bar
    # -------------------------------------------------------------

    def _build_bottom_bar(self) -> None:
        """Subtle bottom status readout."""
        self.bottom_bar = tk.Frame(self.root, bg=self.theme.colors.bg_app, padx=24, pady=6)
        self.bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = tk.Label(
            self.bottom_bar,
            text="Search any location worldwide · Enter to search · F5 to refresh · OpenWeatherMap API",
            font=self.theme.font_caption(),
            fg=self.theme.colors.text_muted,
            bg=self.theme.colors.bg_app
        )
        self.lbl_status.pack(side=tk.LEFT)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<F5>", lambda e: self.refresh_weather())
        self.root.bind("<Escape>", lambda e: self.show_welcome_view())
        # Global mousewheel & keyboard scrolling for dashboard
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel_up)
        self.root.bind_all("<Button-5>", self._on_mousewheel_down)
        self.root.bind_all("<Prior>", self._on_page_up)
        self.root.bind_all("<Next>", self._on_page_down)

    def _on_mousewheel(self, event) -> None:
        """Smooth mousewheel scrolling for the dashboard view."""
        if not self.dashboard_frame.winfo_ismapped():
            return
        if hasattr(self, "dashboard_search_bar") and hasattr(self.dashboard_search_bar, "dropdown"):
            if self.dashboard_search_bar.dropdown.winfo_ismapped():
                return
        content_h = self.dashboard_content.winfo_reqheight()
        canvas_h = self.dashboard_canvas.winfo_height()
        if canvas_h > 1 and content_h > canvas_h:
            import sys
            if sys.platform == "darwin":
                delta = -1 * event.delta
            else:
                delta = -1 * int(event.delta / 120)
            self.dashboard_canvas.yview_scroll(delta, "units")

    def _on_mousewheel_up(self, event) -> None:
        if self.dashboard_frame.winfo_ismapped() and self.dashboard_content.winfo_reqheight() > self.dashboard_canvas.winfo_height():
            self.dashboard_canvas.yview_scroll(-2, "units")

    def _on_mousewheel_down(self, event) -> None:
        if self.dashboard_frame.winfo_ismapped() and self.dashboard_content.winfo_reqheight() > self.dashboard_canvas.winfo_height():
            self.dashboard_canvas.yview_scroll(2, "units")

    def _on_page_up(self, event) -> None:
        if self.dashboard_frame.winfo_ismapped() and not isinstance(self.root.focus_get(), tk.Entry):
            self.dashboard_canvas.yview_scroll(-1, "pages")

    def _on_page_down(self, event) -> None:
        if self.dashboard_frame.winfo_ismapped() and not isinstance(self.root.focus_get(), tk.Entry):
            self.dashboard_canvas.yview_scroll(1, "pages")

    # -------------------------------------------------------------
    # View State Switchers
    # -------------------------------------------------------------

    def _hide_all_views(self) -> None:
        self.welcome_frame.pack_forget()
        self.loading_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.error_frame.pack_forget()

    def show_welcome_view(self) -> None:
        """Display the initial welcome / search portal."""
        self._hide_all_views()
        self.dashboard_search_frame.pack_forget()
        self.btn_home.pack_forget()

        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

    def show_loading_view(self, location_name: str) -> None:
        """Display loading spinner screen."""
        self._hide_all_views()
        self.lbl_loading_city.configure(text=f"Loading weather for {location_name}...")
        self.loading_frame.pack(fill=tk.BOTH, expand=True)

    def show_dashboard_view(self) -> None:
        """Display active workstation dashboard."""
        self._hide_all_views()
        self.dashboard_search_frame.pack(fill=tk.X)
        self.btn_home.pack(side=tk.RIGHT, padx=(8, 0))
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        self.dashboard_canvas.yview_moveto(0.0)
        self.root.after_idle(self._update_dashboard_scroll)

    def show_error_view(self, title: str, description: str) -> None:
        """Display friendly error resolution screen."""
        self._hide_all_views()
        self.dashboard_search_frame.pack_forget()
        self.lbl_error_title.configure(text=title)
        self.lbl_error_desc.configure(text=description)
        self.error_frame.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # State & Network Actions
    # -------------------------------------------------------------

    def _handle_location_select(self, location: Location) -> None:
        """Triggered when user selects a real location from suggestions or recent chips."""
        if self._is_fetching:
            return

        self.current_location = location
        self._is_fetching = True
        self.show_loading_view(location.name)
        self.dashboard_search_bar.set_loading(True)
        self.welcome_search_bar.set_loading(True)

        threading.Thread(
            target=self._worker_fetch_location,
            args=(location, False),
            daemon=True
        ).start()

    def _handle_text_query_submit(self, query: str) -> None:
        """Triggered when user presses Enter on free text without selecting suggestion."""
        clean = query.strip()
        if not clean or self._is_fetching:
            return

        # Resolve query to location
        locations = self.service.search_locations(clean, limit=1)
        if locations:
            self._handle_location_select(locations[0])
            return

        # Fallback to direct name query
        self._is_fetching = True
        self.show_loading_view(clean)
        self.dashboard_search_bar.set_loading(True)
        self.welcome_search_bar.set_loading(True)

        threading.Thread(
            target=self._worker_fetch_name,
            args=(clean, False),
            daemon=True
        ).start()

    def refresh_weather(self) -> None:
        """Force-refresh current location data bypassing local cache."""
        if not self.current_location and not self.current_data:
            self.show_welcome_view()
            return

        target_loc = self.current_location or (self.current_data.location if self.current_data else None)
        if not target_loc or self._is_fetching:
            return

        self._is_fetching = True
        self.show_loading_view(target_loc.name)
        self.dashboard_search_bar.set_loading(True)
        self.welcome_search_bar.set_loading(True)

        threading.Thread(
            target=self._worker_fetch_location,
            args=(target_loc, True),
            daemon=True
        ).start()

    def _worker_fetch_location(self, location: Location, force_refresh: bool) -> None:
        """Background thread worker for coordinate-based weather request."""
        try:
            weather_data = self.service.fetch_weather_by_location(location, force_refresh=force_refresh)
            self.root.after(0, self._on_fetch_success, weather_data)
        except MissingApiKeyError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "API Credentials Missing",
                str(exc)
            )
        except InvalidApiKeyError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Invalid API Key (HTTP 401)",
                str(exc)
            )
        except AuthenticationError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Authentication Error",
                str(exc)
            )
        except CityNotFoundError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Location Not Found (HTTP 404)",
                str(exc) or f"No meteorological records could be found for '{location.display_name}'. Try another city or region."
            )
        except RateLimitError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Rate Limit Exceeded (HTTP 429)",
                str(exc)
            )
        except ServerError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Weather Server Error",
                str(exc)
            )
        except NetworkError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Connection Error",
                str(exc) or "Check your internet connection and try again."
            )
        except TimeoutError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Request Timeout",
                str(exc) or "The weather service took too long to respond. Please try again."
            )
        except WeatherAPIError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Weather Service Error",
                str(exc)
            )
        except Exception as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Unable to Load Weather",
                f"An unexpected issue occurred: {str(exc)}"
            )

    def _worker_fetch_name(self, city_name: str, force_refresh: bool) -> None:
        """Background thread worker for text-based weather request."""
        try:
            weather_data = self.service.fetch_weather(city_name, force_refresh=force_refresh)
            self.root.after(0, self._on_fetch_success, weather_data)
        except MissingApiKeyError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "API Credentials Missing",
                str(exc)
            )
        except InvalidApiKeyError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Invalid API Key (HTTP 401)",
                str(exc)
            )
        except AuthenticationError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Authentication Error",
                str(exc)
            )
        except CityNotFoundError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Location Not Found (HTTP 404)",
                str(exc) or f"No meteorological records found for '{city_name}'. Try another city or region."
            )
        except RateLimitError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Rate Limit Exceeded (HTTP 429)",
                str(exc)
            )
        except ServerError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Weather Server Error",
                str(exc)
            )
        except NetworkError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Connection Error",
                str(exc) or "Check your internet connection and try again."
            )
        except TimeoutError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Request Timeout",
                str(exc) or "The weather service took too long to respond. Please try again."
            )
        except WeatherAPIError as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Weather Service Error",
                str(exc)
            )
        except Exception as exc:
            self.root.after(
                0, self._on_fetch_error,
                "Unable to Load Weather",
                f"An unexpected issue occurred: {str(exc)}"
            )

    def _on_fetch_success(self, data: WeatherData) -> None:
        """Main thread callback on successful API response."""
        self._is_fetching = False
        self.dashboard_search_bar.set_loading(False)
        self.welcome_search_bar.set_loading(False)
        self.current_data = data
        self.current_location = data.location

        # Update search queries and recent list
        self.dashboard_search_bar.set_query(data.location.display_name)
        self.welcome_search_bar.set_query(data.location.display_name)
        self._add_recent_location(data.location)

        # Apply day/night theme variation
        self._apply_day_night_theme(data.is_day)

        # Update Left Hero Panel
        self.lbl_city_title.configure(text=data.location.name)
        self.lbl_region_country.configure(text=data.location.subtitle)
        self.lbl_local_datetime.configure(
            text=f"{data.local_date_str} · {data.local_time_str} Local Time"
        )
        self.hero_icon.set_icon(data.condition, is_day=data.is_day, bg=self.left_hero_card.bg_color)
        self.lbl_hero_temp.configure(text=data.formatted_temp)
        self.lbl_hero_cond.configure(text=data.description)
        self.lbl_feels_like.configure(text=data.formatted_feels_like)
        self.lbl_high_low.configure(text=data.formatted_high_low)

        # Glance metrics
        self.glance_humidity.set(data.metrics.formatted_humidity)
        self.glance_wind.set(f"{round(data.wind.speed_kmh)} km/h · {data.wind.direction}")
        self.glance_visibility.set(data.metrics.formatted_visibility)
        self.glance_pressure.set(data.metrics.formatted_pressure)

        # Update 6 Atmospheric Metric Tiles
        self.tile_wind.update_data(data.wind.formatted_speed, data.wind.formatted_summary)
        self.tile_humidity.update_data(
            data.metrics.formatted_humidity,
            f"{data.metrics.humidity_status} · Dew point {data.metrics.formatted_dew_point}"
        )
        self.tile_pressure.update_data(data.metrics.formatted_pressure, data.metrics.pressure_status)
        self.tile_visibility.update_data(data.metrics.formatted_visibility, data.metrics.visibility_status)
        self.tile_clouds.update_data(data.metrics.formatted_clouds, data.metrics.cloud_status)

        pop_today = data.forecast[0].pop if data.forecast else 0
        precip_note = f"{pop_today}% precipitation chance" if pop_today > 0 else "Dry conditions expected"
        self.tile_dew.update_data(data.metrics.formatted_dew_point, precip_note)

        # Update Sun Arc Widget
        self.sun_arc_widget.update_sun(data.sun)

        # Update Forecast Strip
        for idx, card in enumerate(self.forecast_cards):
            if idx < len(data.forecast):
                card.set_forecast(data.forecast[idx], is_day=True)
                card.grid()
            else:
                card.grid_remove()

        # Update Timestamps
        self.timestamp_lbl.configure(text=f"Updated {data.fetched_at_str}")
        self.lbl_status.configure(
            text=f"Live weather synchronized for {data.location_display} · Source: OpenWeatherMap"
        )

        # Reveal the Dashboard View
        self.show_dashboard_view()

    def _on_fetch_error(self, title: str, description: str) -> None:
        """Main thread callback on error."""
        self._is_fetching = False
        self.dashboard_search_bar.set_loading(False)
        self.welcome_search_bar.set_loading(False)
        self.show_error_view(title, description)
        self.timestamp_lbl.configure(text="Update failed")
        self.lbl_status.configure(text=f"Error: {title}")

    def _add_recent_location(self, loc: Location) -> None:
        """Add location to session recent search history (max 5, MRU)."""
        existing = [l for l in self.recent_locations if l.name.lower() == loc.name.lower() and l.country.lower() == loc.country.lower()]
        for e in existing:
            self.recent_locations.remove(e)
        self.recent_locations.insert(0, loc)
        self.recent_locations = self.recent_locations[:5]

        self.recent_chips.update_locations(self.recent_locations)
        self.welcome_recent_chips.update_locations(self.recent_locations)

    def _apply_day_night_theme(self, is_day: bool) -> None:
        """Subtly adapt visual styling according to local day/night status."""
        self.theme.set_day_mode(is_day)

        if is_day:
            self.day_night_pill.configure(
                text="☼ DAYTIME",
                fg=self.theme.colors.accent,
                bg=self.theme.colors.badge_bg
            )
        else:
            self.day_night_pill.configure(
                text="☾ NIGHTTIME",
                fg=self.theme.colors.accent,
                bg=self.theme.colors.badge_bg
            )

        self.theme.apply_ttk_styles(self.root)
        self.dashboard_frame.configure(bg=self.theme.colors.bg_app)
        self.dashboard_canvas.configure(bg=self.theme.colors.bg_app)
        self.dashboard_content.configure(bg=self.theme.colors.bg_app)
        self.left_hero_card.update_theme(self.theme)
        self.hero_icon.set_canvas_bg(self.left_hero_card.bg_color)
        self.tile_wind.update_theme(self.theme)
        self.tile_humidity.update_theme(self.theme)
        self.tile_pressure.update_theme(self.theme)
        self.tile_visibility.update_theme(self.theme)
        self.tile_clouds.update_theme(self.theme)
        self.tile_dew.update_theme(self.theme)
        self.sun_arc_widget.update_theme(self.theme)
        for card in self.forecast_cards:
            card.update_theme(self.theme)
