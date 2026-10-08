"""Unit tests for the low-level OpenWeatherAPI client with geocoding and coordinates."""

import pytest
from unittest.mock import MagicMock
import requests
from requests.exceptions import Timeout, ConnectionError

from weather_app.core.api import (
    OpenWeatherAPI,
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


@pytest.fixture
def mock_session():
    return MagicMock(spec=requests.Session)


def test_api_key_detection():
    api_without_key = OpenWeatherAPI(api_key="")
    assert not api_without_key.has_api_key

    api_with_key = OpenWeatherAPI(api_key="mock_secret_key")
    assert api_with_key.has_api_key


def test_api_set_api_key():
    api = OpenWeatherAPI(api_key="")
    assert not api.has_api_key
    api.set_api_key("new_key_123")
    assert api.has_api_key


def test_request_without_api_key_raises_auth_error(mock_session):
    api = OpenWeatherAPI(api_key="", session=mock_session)
    with pytest.raises(MissingApiKeyError, match="Weather API credentials are not configured in .env") as exc_info:
        api.get_current_weather_by_coords(51.5074, -0.1278)
    assert isinstance(exc_info.value, AuthenticationError)


def test_empty_city_raises_city_not_found(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    with pytest.raises(CityNotFoundError, match="Please enter a valid city name"):
        api.get_current_weather("   ")

    with pytest.raises(CityNotFoundError, match="Please enter a valid city name"):
        api.get_forecast("")


def test_geocoding_search_locations(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Lahore", "lat": 31.5204, "lon": 74.3587, "country": "PK", "state": "Punjab"},
        {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GB", "state": "England"}
    ]
    mock_session.get.return_value = mock_response

    results = api.search_locations("Lahore", limit=2)
    assert len(results) == 2
    assert results[0]["name"] == "Lahore"
    assert results[0]["country"] == "PK"
    assert results[0]["lat"] == 31.5204


def test_geocoding_empty_query_returns_empty(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    assert api.search_locations("   ") == []


def test_current_weather_by_coords(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Tokyo",
        "coord": {"lat": 35.6762, "lon": 139.6503},
        "main": {"temp": 22.0},
        "weather": [{"main": "Clear"}]
    }
    mock_session.get.return_value = mock_response

    result = api.get_current_weather_by_coords(35.6762, 139.6503)
    assert result["name"] == "Tokyo"
    assert result["main"]["temp"] == 22.0

    call_args = mock_session.get.call_args
    assert call_args[1]["params"]["lat"] == 35.6762
    assert call_args[1]["params"]["lon"] == 139.6503
    assert call_args[1]["params"]["units"] == "metric"


def test_forecast_by_coords(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cnt": 40,
        "list": [{"dt": 1690000000, "main": {"temp": 18.0}}]
    }
    mock_session.get.return_value = mock_response

    result = api.get_forecast_by_coords(40.7128, -74.0060)
    assert result["cnt"] == 40
    assert len(result["list"]) == 1


def test_city_not_found_404_handling(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "city not found"}
    mock_session.get.return_value = mock_response

    with pytest.raises(CityNotFoundError, match="No matching locations found"):
        api.get_current_weather("NonExistentCityXYZ")


def test_unauthorized_401_handling(mock_session):
    api = OpenWeatherAPI(api_key="invalid_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"message": "Invalid API key"}
    mock_session.get.return_value = mock_response

    with pytest.raises(InvalidApiKeyError, match="Weather API credentials are not configured or invalid") as exc_info:
        api.get_current_weather_by_coords(0, 0)
    assert isinstance(exc_info.value, AuthenticationError)


def test_rate_limit_429_handling(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_session.get.return_value = mock_response

    with pytest.raises(RateLimitError, match="API rate limit exceeded") as exc_info:
        api.get_current_weather_by_coords(0, 0)
    assert isinstance(exc_info.value, WeatherAPIError)


def test_server_error_500_handling(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_session.get.return_value = mock_response

    with pytest.raises(ServerError, match="Weather service is temporarily unavailable") as exc_info:
        api.get_current_weather_by_coords(0, 0)
    assert isinstance(exc_info.value, WeatherAPIError)


def test_timeout_handling(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_session.get.side_effect = Timeout("Connection timed out")

    with pytest.raises(TimeoutError, match="took too long to respond"):
        api.get_current_weather_by_coords(0, 0)


def test_network_connection_error_handling(mock_session):
    api = OpenWeatherAPI(api_key="test_key", session=mock_session)
    mock_session.get.side_effect = ConnectionError("DNS failure")

    with pytest.raises(NetworkError, match="Unable to connect to the weather service"):
        api.get_current_weather_by_coords(0, 0)
