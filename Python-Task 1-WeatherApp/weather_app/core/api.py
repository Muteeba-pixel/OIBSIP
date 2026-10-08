"""Low-level HTTP client and error definitions for OpenWeatherMap Geocoding and Weather APIs."""

from typing import Dict, Any, List, Optional
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from .config import get_openweather_api_key


class WeatherAPIError(Exception):
    """Base exception for all weather API related failures."""
    pass


class CityNotFoundError(WeatherAPIError):
    """Raised when the requested city was not found in the database (HTTP 404)."""
    pass


class AuthenticationError(WeatherAPIError):
    """Raised when the API key is missing, unauthorized, or invalid."""
    pass


class MissingApiKeyError(AuthenticationError):
    """Raised when the API key is not configured in .env."""
    pass


class InvalidApiKeyError(AuthenticationError):
    """Raised when the provided API key is rejected by OpenWeatherMap (HTTP 401)."""
    pass


class RateLimitError(WeatherAPIError):
    """Raised when API rate limit has been exceeded (HTTP 429)."""
    pass


class ServerError(WeatherAPIError):
    """Raised when remote weather service responds with HTTP 5xx."""
    pass


class NetworkError(WeatherAPIError):
    """Raised when network connectivity fails."""
    pass


class TimeoutError(WeatherAPIError):
    """Raised when the remote server fails to respond before timeout expiration."""
    pass


class OpenWeatherAPI:
    """HTTP client communicating with OpenWeatherMap Geocoding, Weather, and Forecast endpoints."""

    DATA_BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0"
    DEFAULT_TIMEOUT_SECONDS = 10.0

    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: Optional API key. If not provided, reads from centralized config (OPENWEATHER_API_KEY).
            session: Optional custom requests.Session for pooling or unit testing.
        """
        if api_key is not None:
            self._api_key = api_key.strip()
        else:
            self._api_key = get_openweather_api_key()
        self._session = session or requests.Session()

    @property
    def has_api_key(self) -> bool:
        """Check whether an API key has been configured without exposing its contents."""
        return bool(self._api_key and self._api_key.strip())

    def set_api_key(self, api_key: str) -> None:
        """Update or set the API key."""
        self._api_key = api_key.strip() if api_key else ""

    def _execute_request(self, url: str, params: Dict[str, Any]) -> Any:
        """Execute HTTP request with strict error translation and timeout handling."""
        if not self.has_api_key:
            raise MissingApiKeyError("Weather API credentials are not configured in .env. Please define OPENWEATHER_API_KEY.")

        request_params = {
            "appid": self._api_key,
            **params
        }

        try:
            response = self._session.get(url, params=request_params, timeout=self.DEFAULT_TIMEOUT_SECONDS)
        except Timeout as exc:
            raise TimeoutError("The weather service took too long to respond (timeout).") from exc
        except ConnectionError as exc:
            raise NetworkError("Unable to connect to the weather service. Check your internet connection.") from exc
        except RequestException as exc:
            raise WeatherAPIError("Weather service network request failed.") from exc

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            raise CityNotFoundError("No matching locations found (HTTP 404). Try another city or region.")

        if response.status_code == 401:
            detail = ""
            try:
                detail = response.json().get("message", "")
            except Exception:
                pass
            msg = f"Weather API credentials are not configured or invalid (HTTP 401): {detail}" if detail else "Weather API credentials are not configured or invalid (HTTP 401)."
            raise InvalidApiKeyError(msg)

        if response.status_code == 429:
            raise RateLimitError("API rate limit exceeded (HTTP 429). Please wait a moment and try again.")

        if response.status_code >= 500:
            raise ServerError(f"Weather service is temporarily unavailable (HTTP {response.status_code}). Please try again later.")

        try:
            error_data = response.json()
            message = error_data.get("message", f"Request failed with HTTP {response.status_code}")
        except Exception:
            message = f"Request failed with HTTP {response.status_code}"

        raise WeatherAPIError(message)

    def search_locations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query OpenWeatherMap Geocoding API to resolve a location search string to real geographic coordinates.
        
        Args:
            query: Location query (e.g., 'Lahore', 'Tokyo', 'London', 'New York', 'Paris')
            limit: Maximum count of results (default 5)
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        url = f"{self.GEO_BASE_URL}/direct"
        result = self._execute_request(url, {"q": clean_query, "limit": limit})
        return result if isinstance(result, list) else []

    def get_current_weather_by_coords(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather by exact coordinates in metric units."""
        url = f"{self.DATA_BASE_URL}/weather"
        return self._execute_request(url, {"lat": lat, "lon": lon, "units": "metric"})

    def get_forecast_by_coords(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch 5-day / 3-hour forecast by exact coordinates in metric units."""
        url = f"{self.DATA_BASE_URL}/forecast"
        return self._execute_request(url, {"lat": lat, "lon": lon, "units": "metric"})

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Fetch current weather by city name."""
        clean_city = city.strip()
        if not clean_city:
            raise CityNotFoundError("Please enter a valid city name.")
        url = f"{self.DATA_BASE_URL}/weather"
        return self._execute_request(url, {"q": clean_city, "units": "metric"})

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Fetch forecast by city name."""
        clean_city = city.strip()
        if not clean_city:
            raise CityNotFoundError("Please enter a valid city name.")
        url = f"{self.DATA_BASE_URL}/forecast"
        return self._execute_request(url, {"q": clean_city, "units": "metric"})
