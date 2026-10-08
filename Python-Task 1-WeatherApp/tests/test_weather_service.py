"""Unit tests for the WeatherService business logic, location search, caching, and forecast aggregation."""

import pytest
from unittest.mock import MagicMock

from weather_app.core.weather_service import WeatherService
from weather_app.core.api import OpenWeatherAPI
from weather_app.core.utils import WeatherCache
from weather_app.core.models import Location, WeatherData, ForecastDay


@pytest.fixture
def sample_location():
    return Location("Lahore", 31.5204, 74.3587, "PK", "Punjab")


@pytest.fixture
def sample_current_raw():
    return {
        "name": "Lahore",
        "coord": {"lat": 31.5204, "lon": 74.3587},
        "sys": {
            "country": "PK",
            "sunrise": 1696554000,
            "sunset": 1696596000
        },
        "main": {
            "temp": 28.6,
            "feels_like": 30.2,
            "temp_min": 26.0,
            "temp_max": 31.0,
            "pressure": 1012,
            "humidity": 62
        },
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d"
            }
        ],
        "wind": {
            "speed": 3.8,  # m/s -> ~13.7 km/h
            "deg": 310,
            "gust": 5.5
        },
        "visibility": 10000,
        "clouds": {"all": 15},
        "dt": 1696570000,
        "timezone": 18000  # UTC+5
    }


@pytest.fixture
def sample_forecast_raw():
    return {
        "cnt": 3,
        "list": [
            {
                "dt": 1696570000,  # Day 1
                "main": {"temp": 28.0, "temp_min": 26.0, "temp_max": 29.0, "humidity": 60},
                "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                "wind": {"speed": 3.0},
                "pop": 0.0
            },
            {
                "dt": 1696580000,  # Day 1 afternoon
                "main": {"temp": 31.0, "temp_min": 29.0, "temp_max": 32.0, "humidity": 50},
                "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                "wind": {"speed": 4.0},
                "pop": 0.1
            },
            {
                "dt": 1696660000,  # Day 2
                "main": {"temp": 25.0, "temp_min": 22.0, "temp_max": 27.0, "humidity": 75},
                "weather": [{"main": "Rain", "description": "moderate rain", "icon": "10d"}],
                "wind": {"speed": 5.0},
                "pop": 0.8
            }
        ]
    }


def test_fetch_weather_empty_city_raises_value_error():
    service = WeatherService(api=MagicMock())
    with pytest.raises(ValueError, match="City name must not be empty"):
        service.fetch_weather("  ")


def test_search_locations_country_query():
    service = WeatherService(api=MagicMock())
    results = service.search_locations("Pakistan")
    assert len(results) >= 4
    names = [r.name for r in results]
    assert "Islamabad" in names
    assert "Lahore" in names
    assert all(r.country == "PK" for r in results)


def test_search_locations_geocoding_api():
    mock_api = MagicMock(spec=OpenWeatherAPI)
    mock_api.has_api_key = True
    mock_api.search_locations.return_value = [
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "country": "JP", "state": "Tokyo"}
    ]
    service = WeatherService(api=mock_api)
    results = service.search_locations("Tokyo")

    assert len(results) == 1
    assert results[0].name == "Tokyo"
    assert results[0].lat == 35.6762
    assert results[0].country == "JP"


def test_search_locations_offline_fallback():
    mock_api = MagicMock(spec=OpenWeatherAPI)
    mock_api.has_api_key = False
    service = WeatherService(api=mock_api)

    results = service.search_locations("lah")
    assert len(results) >= 1
    assert results[0].name == "Lahore"


def test_fetch_weather_by_location_success(sample_location, sample_current_raw, sample_forecast_raw):
    mock_api = MagicMock(spec=OpenWeatherAPI)
    mock_api.get_current_weather_by_coords.return_value = sample_current_raw
    mock_api.get_forecast_by_coords.return_value = sample_forecast_raw

    cache = WeatherCache()
    service = WeatherService(api=mock_api, cache=cache)

    result = service.fetch_weather_by_location(sample_location)

    assert isinstance(result, WeatherData)
    assert result.city_name == "Lahore"
    assert result.country == "PK"
    assert result.location.name == "Lahore"
    assert result.formatted_temp == "29°C"
    assert result.condition == "Clear"
    assert result.description == "Clear Sky"
    assert round(result.wind.speed_kmh) == 14
    assert result.wind.direction == "NW"
    assert result.metrics.humidity == 62
    assert result.metrics.pressure == 1012
    assert result.metrics.visibility_km == 10.0
    assert result.sun.daylight_duration != "--"
    assert len(result.forecast) == 2

    # Verify cache was populated by coordinate key
    cache_key = f"{round(sample_location.lat, 3)}_{round(sample_location.lon, 3)}"
    assert cache.get(cache_key) is result


def test_caching_avoids_redundant_api_calls(sample_location, sample_current_raw, sample_forecast_raw):
    mock_api = MagicMock(spec=OpenWeatherAPI)
    mock_api.get_current_weather_by_coords.return_value = sample_current_raw
    mock_api.get_forecast_by_coords.return_value = sample_forecast_raw

    service = WeatherService(api=mock_api, cache=WeatherCache())

    # Call 1: triggers API
    res1 = service.fetch_weather_by_location(sample_location)
    assert mock_api.get_current_weather_by_coords.call_count == 1
    assert mock_api.get_forecast_by_coords.call_count == 1

    # Call 2: reads from cache
    res2 = service.fetch_weather_by_location(sample_location)
    assert res1 is res2
    assert mock_api.get_current_weather_by_coords.call_count == 1
    assert mock_api.get_forecast_by_coords.call_count == 1


def test_force_refresh_bypasses_cache(sample_location, sample_current_raw, sample_forecast_raw):
    mock_api = MagicMock(spec=OpenWeatherAPI)
    mock_api.get_current_weather_by_coords.return_value = sample_current_raw
    mock_api.get_forecast_by_coords.return_value = sample_forecast_raw

    service = WeatherService(api=mock_api, cache=WeatherCache())

    # First fetch
    service.fetch_weather_by_location(sample_location)
    assert mock_api.get_current_weather_by_coords.call_count == 1

    # Force refresh
    service.fetch_weather_by_location(sample_location, force_refresh=True)
    assert mock_api.get_current_weather_by_coords.call_count == 2
    assert mock_api.get_forecast_by_coords.call_count == 2


def test_forecast_aggregation_daily_metrics(sample_forecast_raw):
    service = WeatherService(api=MagicMock())
    tz_offset = 18000
    current_unix = 1696570000

    forecast_days = service._aggregate_forecast(
        sample_forecast_raw["list"],
        tz_offset=tz_offset,
        current_unix=current_unix
    )

    assert len(forecast_days) == 2

    day1 = forecast_days[0]
    assert day1.day_name == "Today"
    assert day1.temp_max == 32.0
    assert day1.temp_min == 26.0
    assert day1.pop == 10

    day2 = forecast_days[1]
    assert day2.condition == "Rain"
    assert day2.temp_max == 27.0
    assert day2.temp_min == 22.0
    assert day2.pop == 80


def test_empty_forecast_aggregation():
    service = WeatherService(api=MagicMock())
    result = service._aggregate_forecast([], 0, 0)
    assert result == []
