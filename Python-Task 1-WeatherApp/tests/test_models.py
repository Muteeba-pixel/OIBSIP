"""Unit tests for Location and weather data models."""

import pytest
from weather_app.core.models import (
    Location,
    WindInfo,
    SunTimes,
    AtmosphericMetrics,
    ForecastDay,
    WeatherData,
)


def test_location_model_properties():
    loc1 = Location(name="Lahore", lat=31.5204, lon=74.3587, country="PK", state="Punjab")
    assert loc1.name == "Lahore"
    assert loc1.lat == 31.5204
    assert loc1.lon == 74.3587
    assert loc1.country == "PK"
    assert loc1.country_full_name == "Pakistan"
    assert loc1.display_name == "Lahore, Punjab, Pakistan"
    assert loc1.subtitle == "Punjab, Pakistan"

    loc2 = Location(name="Tokyo", lat=35.6762, lon=139.6503, country="JP", state="Tokyo")
    # State matches name, avoids repetition in display
    assert loc2.display_name == "Tokyo, Japan"
    assert loc2.subtitle == "Japan"

    loc3 = Location(name="Singapore", lat=1.3521, lon=103.8198, country="SG", state=None)
    assert loc3.country_full_name == "Singapore"
    assert loc3.display_name == "Singapore, Singapore"


def test_wind_info_properties():
    wind = WindInfo(
        speed_kmh=14.4,
        deg=315,
        direction="NW",
        gust_kmh=22.1,
        beaufort_desc="Gentle breeze"
    )
    assert wind.formatted_speed == "14 km/h"
    assert wind.formatted_full == "14 km/h · NW (315°)"
    assert wind.gust_kmh == 22.1
    assert "Gentle breeze" in wind.formatted_summary
    assert "Gust 22 km/h" in wind.formatted_summary


def test_atmospheric_metrics_formatting():
    metrics = AtmosphericMetrics(
        humidity=65,
        pressure=1014,
        visibility_km=10.0,
        cloudiness=25,
        dew_point_c=12.4
    )
    assert metrics.formatted_humidity == "65%"
    assert metrics.formatted_pressure == "1014 hPa"
    assert metrics.formatted_visibility == "10 km"
    assert metrics.formatted_clouds == "25%"
    assert metrics.dew_point_c == 12.4
    assert metrics.formatted_dew_point == "12°C"


def test_forecast_day_properties():
    day = ForecastDay(
        date_str="Oct 07",
        day_name="Mon",
        condition="Rain",
        description="Light Rain",
        icon_code="10d",
        temp_max=24.8,
        temp_min=17.2,
        pop=60,
        humidity_avg=78,
        wind_speed_avg=12.0
    )
    assert day.formatted_temp_range == "25° / 17°"
    assert day.formatted_high == "25°"
    assert day.formatted_low == "17°"
    assert day.pop == 60


def test_weather_data_properties():
    loc = Location("Islamabad", 33.6844, 73.0479, "PK", "Islamabad Capital Territory")
    wind = WindInfo(speed_kmh=10.0, deg=90, direction="E")
    sun = SunTimes(
        sunrise_unix=1690000000,
        sunset_unix=1690045000,
        sunrise_local="05:30 AM",
        sunset_local="06:45 PM",
        daylight_duration="13h 15m",
        is_day=True,
        solar_progress=0.4
    )
    metrics = AtmosphericMetrics(
        humidity=50,
        pressure=1012,
        visibility_km=10.0,
        cloudiness=10
    )

    data = WeatherData(
        location=loc,
        temp=28.4,
        feels_like=29.7,
        temp_min=22.0,
        temp_max=30.0,
        condition="Clear",
        description="Clear Sky",
        icon_code="01d",
        wind=wind,
        sun=sun,
        metrics=metrics,
        timezone_offset=18000,
        local_time_str="03:00 PM",
        local_date_str="Monday, Oct 6, 2026",
        fetched_at_str="11:00 AM",
        forecast=[]
    )

    assert data.city_name == "Islamabad"
    assert data.country == "PK"
    assert data.location_display == "Islamabad, Islamabad Capital Territory, Pakistan"
    assert data.formatted_temp == "28°C"
    assert data.formatted_feels_like == "Feels like 30°C"
    assert data.formatted_high_low == "High 30°   Low 22°"
    assert data.is_day is True
