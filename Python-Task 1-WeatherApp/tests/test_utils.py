"""Unit tests for meteorological utilities, formatting, and cache management."""

import time
import os
import tempfile
import pytest
from weather_app.core.utils import (
    deg_to_compass,
    ms_to_kmh,
    wind_beaufort_description,
    calculate_dew_point,
    humidity_comfort_level,
    pressure_level_description,
    visibility_description,
    cloud_coverage_description,
    calculate_daylight_duration,
    calculate_solar_progress,
    is_daytime,
    format_condition_title,
    search_country_locations,
    search_offline_locations,
    WeatherCache,
)


def test_deg_to_compass_cardinal_points():
    assert deg_to_compass(0) == "N"
    assert deg_to_compass(360) == "N"
    assert deg_to_compass(90) == "E"
    assert deg_to_compass(180) == "S"
    assert deg_to_compass(270) == "W"


def test_deg_to_compass_intercardinal_points():
    assert deg_to_compass(45) == "NE"
    assert deg_to_compass(135) == "SE"
    assert deg_to_compass(225) == "SW"
    assert deg_to_compass(315) == "NW"


def test_deg_to_compass_boundary_and_wraparound():
    assert deg_to_compass(350) == "N"
    assert deg_to_compass(720) == "N"
    assert deg_to_compass(450) == "E"


def test_ms_to_kmh():
    assert ms_to_kmh(0) == 0.0
    assert ms_to_kmh(10) == 36.0
    assert ms_to_kmh(5.555) == 20.0


def test_wind_beaufort_description():
    assert wind_beaufort_description(1.0) == "Calm"
    assert wind_beaufort_description(4.0) == "Light air"
    assert wind_beaufort_description(8.0) == "Light breeze"
    assert wind_beaufort_description(15.0) == "Gentle breeze"
    assert wind_beaufort_description(25.0) == "Moderate breeze"
    assert wind_beaufort_description(35.0) == "Fresh breeze"
    assert wind_beaufort_description(55.0) == "High wind"


def test_calculate_dew_point():
    dew_point = calculate_dew_point(temp_c=25.0, humidity_pct=60.0)
    assert 16.0 <= dew_point <= 18.0

    # Zero humidity boundary
    assert calculate_dew_point(temp_c=20.0, humidity_pct=0.0) == 20.0


def test_qualitative_helpers():
    assert humidity_comfort_level(20) == "Dry air"
    assert humidity_comfort_level(50) == "Comfortable"
    assert humidity_comfort_level(85) == "High humidity"

    assert pressure_level_description(995) == "Low pressure system"
    assert pressure_level_description(1013) == "Normal atmospheric level"
    assert pressure_level_description(1030) == "High pressure system"

    assert visibility_description(10.0) == "Clear horizon"
    assert visibility_description(5.0) == "Good visibility"
    assert visibility_description(1.0) == "Dense fog / mist"

    assert cloud_coverage_description(5) == "Clear sky"
    assert cloud_coverage_description(50) == "Partly cloudy"
    assert cloud_coverage_description(90) == "Overcast"


def test_calculate_daylight_duration():
    sunrise = 100000
    sunset = 100000 + 45000
    duration = calculate_daylight_duration(sunrise, sunset)
    assert duration == "12h 30m"


def test_calculate_solar_progress():
    sunrise = 1000
    sunset = 2000

    # Nighttime before sunrise
    assert calculate_solar_progress(500, sunrise, sunset) == -1.0
    # At sunrise
    assert calculate_solar_progress(1000, sunrise, sunset) == 0.0
    # Halfway
    assert calculate_solar_progress(1500, sunrise, sunset) == 0.5
    # At sunset
    assert calculate_solar_progress(2000, sunrise, sunset) == 1.0
    # Nighttime after sunset
    assert calculate_solar_progress(2500, sunrise, sunset) == -1.0


def test_is_daytime():
    sunrise = 1000
    sunset = 2000

    assert is_daytime(500, sunrise, sunset) is False
    assert is_daytime(1000, sunrise, sunset) is True
    assert is_daytime(1500, sunrise, sunset) is True
    assert is_daytime(2000, sunrise, sunset) is True
    assert is_daytime(2500, sunrise, sunset) is False


def test_format_condition_title():
    assert format_condition_title("scattered clouds") == "Scattered Clouds"
    assert format_condition_title("light intensity shower rain") == "Light Intensity Shower Rain"
    assert format_condition_title("") == "Unknown"


def test_search_country_locations():
    # Pakistan aliases
    pk_results = search_country_locations("Pakistan")
    assert pk_results is not None
    assert len(pk_results) >= 4
    pk_names = [l.name for l in pk_results]
    assert "Islamabad" in pk_names
    assert "Lahore" in pk_names
    assert "Karachi" in pk_names

    # USA aliases
    us_results = search_country_locations("USA")
    assert us_results is not None
    us_names = [l.name for l in us_results]
    assert "New York" in us_names

    # Non-country query
    assert search_country_locations("nonexistentcountry123") is None


def test_search_offline_locations():
    results = search_offline_locations("lah", limit=5)
    assert any(l.name == "Lahore" for l in results)

    results_tokyo = search_offline_locations("tok", limit=5)
    assert any(l.name == "Tokyo" for l in results_tokyo)

    # Empty query
    assert search_offline_locations("") == []


def test_weather_cache_basic_operations():
    cache = WeatherCache(default_ttl_seconds=10)
    assert cache.get("London") is None

    cache.set("London", {"temp": 18})
    assert cache.get("London") == {"temp": 18}

    assert cache.get("london") == {"temp": 18}
    assert cache.get("  LONDON  ") == {"temp": 18}


def test_weather_cache_invalidation():
    cache = WeatherCache(default_ttl_seconds=10)
    cache.set("Paris", "sunny")
    assert cache.get("Paris") == "sunny"

    cache.invalidate("paris")
    assert cache.get("Paris") is None


def test_weather_cache_expiration():
    cache = WeatherCache(default_ttl_seconds=1)
    cache.set("Tokyo", "rainy", ttl_seconds=0)
    time.sleep(0.01)
    assert cache.get("Tokyo") is None


def test_weather_cache_clear():
    cache = WeatherCache()
    cache.set("CityA", 1)
    cache.set("CityB", 2)
    cache.clear()
    assert cache.get("CityA") is None
    assert cache.get("CityB") is None
