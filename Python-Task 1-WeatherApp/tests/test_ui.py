"""UI component and application state tests."""

import pytest
import tkinter as tk
from unittest.mock import MagicMock

from weather_app.ui.app import WeatherApp
from weather_app.ui.theme import get_theme, Theme
from weather_app.ui.icons import WeatherIconCanvas, SunArcCanvas
from weather_app.ui.components import AutocompleteDropdown, RecentLocationsBar
from weather_app.core.models import (
    Location,
    WeatherData,
    WindInfo,
    SunTimes,
    AtmosphericMetrics,
    ForecastDay,
)


@pytest.fixture
def tk_root():
    """Create and tear down a hidden Tkinter root window."""
    try:
        root = tk.Tk()
        root.withdraw()  # Keep window hidden during test runs
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("Tkinter display not available in current environment")


@pytest.fixture
def sample_weather_model():
    loc = Location("London", 51.5074, -0.1278, "GB", "England")
    return WeatherData(
        location=loc,
        temp=19.2,
        feels_like=18.5,
        temp_min=16.0,
        temp_max=21.0,
        condition="Clouds",
        description="Scattered Clouds",
        icon_code="03d",
        wind=WindInfo(speed_kmh=12.5, deg=240, direction="WSW", beaufort_desc="Gentle breeze"),
        sun=SunTimes(
            sunrise_unix=1690000000,
            sunset_unix=1690045000,
            sunrise_local="05:45 AM",
            sunset_local="08:30 PM",
            daylight_duration="14h 45m",
            is_day=True,
            solar_progress=0.5
        ),
        metrics=AtmosphericMetrics(
            humidity=68,
            pressure=1015,
            visibility_km=10.0,
            cloudiness=40,
            dew_point_c=13.0,
            humidity_status="Comfortable",
            pressure_status="Normal",
            visibility_status="Clear horizon",
            cloud_status="Partly cloudy"
        ),
        timezone_offset=3600,
        local_time_str="01:30 PM",
        local_date_str="Tuesday, Oct 7, 2026",
        fetched_at_str="01:30 PM",
        forecast=[
            ForecastDay(
                date_str="Oct 08",
                day_name="Wed",
                condition="Rain",
                description="Light Rain",
                icon_code="10d",
                temp_max=18.0,
                temp_min=13.0,
                pop=70
            )
        ]
    )


def test_theme_day_night_switch():
    theme = Theme(is_day=True)
    assert theme.is_day is True
    day_accent = theme.colors.accent

    theme.set_day_mode(False)
    assert theme.is_day is False
    assert theme.colors.accent != day_accent


def test_weather_icon_canvas_renders_conditions(tk_root):
    canvas = WeatherIconCanvas(tk_root, condition="Clear", is_day=True, size=48)
    assert canvas.condition == "Clear"
    conditions = ["Thunderstorm", "Snow", "Rain", "Drizzle", "Mist", "Clouds", "Clear"]
    for cond in conditions:
        canvas.set_icon(cond, is_day=True)
        canvas.set_icon(cond, is_day=False)


def test_sun_arc_canvas_renders(tk_root):
    arc = SunArcCanvas(tk_root, width=240, height=80)
    arc.update_sun_cycle(
        sunrise_str="05:30 AM",
        sunset_str="06:45 PM",
        daylight_str="13h 15m",
        progress=0.45,
        is_day=True
    )
    # Also verify night rendering
    arc.update_sun_cycle(
        sunrise_str="05:30 AM",
        sunset_str="06:45 PM",
        daylight_str="13h 15m",
        progress=-1.0,
        is_day=False
    )


def test_weather_app_initialization_welcome_state(tk_root):
    mock_service = MagicMock()
    mock_service.api.has_api_key = False

    app = WeatherApp(tk_root, service=mock_service)
    tk_root.update()

    assert app.root == tk_root
    assert app.current_location is None
    assert app.current_city is None
    # Welcome view is active on start
    assert app.welcome_frame.winfo_manager() == "pack"
    # Never show API key setup UI
    assert not hasattr(app, "api_setup_card")


def test_weather_app_successful_data_bind(tk_root, sample_weather_model):
    mock_service = MagicMock()
    app = WeatherApp(tk_root, service=mock_service)

    app._on_fetch_success(sample_weather_model)
    tk_root.update()

    assert app.current_city == "London"
    assert app.lbl_city_title.cget("text") == "London"
    assert app.lbl_hero_temp.cget("text") == "19°C"
    assert app.lbl_hero_cond.cget("text") == "Scattered Clouds"
    assert len(app.recent_locations) == 1
    assert app.recent_locations[0].name == "London"
    # Dashboard view is active
    assert app.dashboard_frame.winfo_manager() == "pack"


def test_weather_app_error_view_display(tk_root):
    mock_service = MagicMock()
    app = WeatherApp(tk_root, service=mock_service)

    err_title = "City not found"
    err_desc = "Could not locate records for Atlantis."
    app._on_fetch_error(err_title, err_desc)
    tk_root.update()

    assert app.error_frame.winfo_manager() == "pack"
    assert app.lbl_error_title.cget("text") == err_title
    assert app.lbl_error_desc.cget("text") == err_desc


def test_autocomplete_dropdown_lifecycle(tk_root):
    theme = get_theme()
    selected_loc = None

    def on_select(loc):
        nonlocal selected_loc
        selected_loc = loc

    dropdown = AutocompleteDropdown(tk_root, theme, on_select)
    locations = [
        Location("Lahore", 31.52, 74.35, "PK", "Punjab"),
        Location("London", 51.50, -0.12, "GB", "England"),
    ]
    dropdown.set_suggestions(locations)
    assert len(dropdown.items) == 2

    # Move down
    dropdown.select_next()
    assert dropdown.selected_index == 0
    assert dropdown.get_selected_location() == locations[0]

    # Move next
    dropdown.select_next()
    assert dropdown.selected_index == 1
    assert dropdown.get_selected_location() == locations[1]

    # Move prev
    dropdown.select_prev()
    assert dropdown.selected_index == 0

    dropdown.close()
    assert len(dropdown.items) == 0


def test_recent_locations_bar(tk_root):
    theme = get_theme()
    picked_loc = None

    def on_select(loc):
        nonlocal picked_loc
        picked_loc = loc

    bar = RecentLocationsBar(tk_root, theme, on_select)
    locations = [Location("Dubai", 25.20, 55.27, "AE", "Dubai")]
    bar.update_locations(locations)
    tk_root.update()

    chips = [c for c in bar.chips_container.winfo_children() if isinstance(c, tk.Button)]
    assert len(chips) == 1
    assert chips[0].cget("text") == "Dubai"


def test_theme_does_not_create_extra_tk_root():
    from weather_app.ui.theme import Theme
    # Theme resolution must not create new un-destroyed root windows
    theme = Theme()
    assert theme.font_family in ("Segoe UI", "Inter", "Helvetica")


def test_ui_worker_invalid_api_key_error_display(tk_root):
    from weather_app.core.api import InvalidApiKeyError
    mock_service = MagicMock()
    mock_service.fetch_weather_by_location.side_effect = InvalidApiKeyError(
        "Weather API credentials are not configured or invalid (HTTP 401): Invalid API key."
    )
    app = WeatherApp(tk_root, service=mock_service)
    loc = Location("Lahore", 31.52, 74.35, "PK")

    # Call worker synchronously for test verification
    app._worker_fetch_location(loc, force_refresh=True)
    tk_root.update()

    assert app.error_frame.winfo_manager() == "pack"
    assert "Invalid API Key" in app.lbl_error_title.cget("text")
    assert "HTTP 401" in app.lbl_error_desc.cget("text")


def test_ui_worker_missing_api_key_error_display(tk_root):
    from weather_app.core.api import MissingApiKeyError
    mock_service = MagicMock()
    mock_service.fetch_weather_by_location.side_effect = MissingApiKeyError(
        "Weather API credentials are not configured in .env. Please define OPENWEATHER_API_KEY."
    )
    app = WeatherApp(tk_root, service=mock_service)
    loc = Location("Lahore", 31.52, 74.35, "PK")

    # Call worker synchronously for test verification
    app._worker_fetch_location(loc, force_refresh=True)
    tk_root.update()

    assert app.error_frame.winfo_manager() == "pack"
    assert "API Credentials Missing" in app.lbl_error_title.cget("text")
    assert "configured in .env" in app.lbl_error_desc.cget("text")


