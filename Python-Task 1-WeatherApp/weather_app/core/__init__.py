"""Core package for Atmos Weather Desk containing API client, models, and service layer."""

from .models import (
    Location,
    WeatherData,
    ForecastDay,
    WindInfo,
    SunTimes,
    AtmosphericMetrics,
)
from .api import (
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
from .config import load_app_config, get_openweather_api_key, has_openweather_api_key
from .weather_service import WeatherService

__all__ = [
    "Location",
    "WeatherData",
    "ForecastDay",
    "WindInfo",
    "SunTimes",
    "AtmosphericMetrics",
    "OpenWeatherAPI",
    "WeatherAPIError",
    "CityNotFoundError",
    "AuthenticationError",
    "MissingApiKeyError",
    "InvalidApiKeyError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    "WeatherService",
    "load_app_config",
    "get_openweather_api_key",
    "has_openweather_api_key",
]
