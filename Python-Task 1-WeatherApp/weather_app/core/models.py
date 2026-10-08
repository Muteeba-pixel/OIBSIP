"""Data models for structured weather intelligence and geographic locations."""

from dataclasses import dataclass, field
from typing import List, Optional


# ISO 3166-1 alpha-2 country code dictionary for professional display
ISO_COUNTRY_NAMES = {
    "AF": "Afghanistan", "AL": "Albania", "DZ": "Algeria", "AR": "Argentina",
    "AU": "Australia", "AT": "Austria", "BD": "Bangladesh", "BE": "Belgium",
    "BR": "Brazil", "CA": "Canada", "CH": "Switzerland", "CL": "Chile",
    "CN": "China", "CO": "Colombia", "CZ": "Czech Republic", "DE": "Germany",
    "DK": "Denmark", "EG": "Egypt", "ES": "Spain", "FI": "Finland",
    "FR": "France", "GB": "United Kingdom", "GR": "Greece", "HK": "Hong Kong",
    "ID": "Indonesia", "IE": "Ireland", "IL": "Israel", "IN": "India",
    "IQ": "Iraq", "IR": "Iran", "IT": "Italy", "JP": "Japan",
    "KR": "South Korea", "KW": "Kuwait", "MX": "Mexico", "MY": "Malaysia",
    "NL": "Netherlands", "NO": "Norway", "NZ": "New Zealand", "OM": "Oman",
    "PK": "Pakistan", "PH": "Philippines", "PL": "Poland", "PT": "Portugal",
    "QA": "Qatar", "RU": "Russia", "SA": "Saudi Arabia", "SE": "Sweden",
    "SG": "Singapore", "TH": "Thailand", "TR": "Turkey", "UA": "Ukraine",
    "AE": "United Arab Emirates", "US": "United States", "VN": "Vietnam",
    "ZA": "South Africa"
}


@dataclass(frozen=True)
class Location:
    """Exact geographic location entity with coordinates and regional hierarchy."""
    name: str                       # e.g., "Lahore", "Tokyo", "London"
    lat: float                      # Latitude
    lon: float                      # Longitude
    country: str                    # Country code or name e.g., "PK", "GB", "US"
    state: Optional[str] = None     # State/province/region e.g., "Punjab", "England"

    @property
    def country_full_name(self) -> str:
        """Resolve ISO country code to full name if applicable."""
        upper = self.country.strip().upper()
        return ISO_COUNTRY_NAMES.get(upper, self.country.strip())

    @property
    def display_name(self) -> str:
        """Formatted title e.g., 'Lahore, Punjab, Pakistan'."""
        parts = [self.name]
        if self.state and self.state.strip().lower() != self.name.strip().lower():
            parts.append(self.state.strip())
        country_name = self.country_full_name
        if country_name:
            parts.append(country_name)
        return ", ".join(parts)

    @property
    def subtitle(self) -> str:
        """Subtitle hierarchy e.g., 'Punjab, Pakistan'."""
        parts = []
        if self.state and self.state.strip().lower() != self.name.strip().lower():
            parts.append(self.state.strip())
        country_name = self.country_full_name
        if country_name:
            parts.append(country_name)
        return ", ".join(parts) if parts else self.name


@dataclass(frozen=True)
class WindInfo:
    """Wind velocity and compass direction."""
    speed_kmh: float
    deg: int
    direction: str
    gust_kmh: Optional[float] = None
    beaufort_desc: str = "Moderate breeze"

    @property
    def formatted_speed(self) -> str:
        return f"{round(self.speed_kmh)} km/h"

    @property
    def formatted_full(self) -> str:
        return f"{round(self.speed_kmh)} km/h · {self.direction} ({self.deg}°)"

    @property
    def formatted_summary(self) -> str:
        gust = f" · Gust {round(self.gust_kmh)} km/h" if self.gust_kmh else ""
        return f"{self.direction} ({self.deg}°) · {self.beaufort_desc}{gust}"


@dataclass(frozen=True)
class SunTimes:
    """Solar cycle schedule converted to local city time."""
    sunrise_unix: int
    sunset_unix: int
    sunrise_local: str
    sunset_local: str
    daylight_duration: str
    is_day: bool
    solar_progress: float = 0.5


@dataclass(frozen=True)
class AtmosphericMetrics:
    """Atmospheric and environmental measurements."""
    humidity: int          # Percentage 0-100
    pressure: int          # hPa
    visibility_km: float   # Kilometers
    cloudiness: int        # Percentage 0-100
    dew_point_c: Optional[float] = None
    humidity_status: str = "Comfortable"
    pressure_status: str = "Normal"
    visibility_status: str = "Clear horizon"
    cloud_status: str = "Partly cloudy"

    @property
    def formatted_visibility(self) -> str:
        if self.visibility_km >= 10:
            return f"{self.visibility_km:.0f} km"
        return f"{self.visibility_km:.1f} km"

    @property
    def formatted_pressure(self) -> str:
        return f"{self.pressure} hPa"

    @property
    def formatted_humidity(self) -> str:
        return f"{self.humidity}%"

    @property
    def formatted_clouds(self) -> str:
        return f"{self.cloudiness}%"

    @property
    def formatted_dew_point(self) -> str:
        if self.dew_point_c is not None:
            return f"{round(self.dew_point_c)}°C"
        return "--"


@dataclass(frozen=True)
class ForecastDay:
    """Aggregated daily forecast derived from 3-hour interval slices."""
    date_str: str          # e.g., "Oct 07"
    day_name: str          # e.g., "Today", "Mon", "Tue"
    condition: str         # e.g., "Clear", "Clouds", "Rain"
    description: str       # e.g., "Scattered Clouds"
    icon_code: str         # e.g., "01d", "10d"
    temp_max: float        # Celsius
    temp_min: float        # Celsius
    pop: int               # Probability of precipitation (0-100%)
    humidity_avg: int = 0
    wind_speed_avg: float = 0.0

    @property
    def formatted_temp_range(self) -> str:
        return f"{round(self.temp_max)}° / {round(self.temp_min)}°"

    @property
    def formatted_high(self) -> str:
        return f"{round(self.temp_max)}°"

    @property
    def formatted_low(self) -> str:
        return f"{round(self.temp_min)}°"


@dataclass
class WeatherData:
    """Complete consolidated weather station dataset for an exact queried location."""
    location: Location
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    condition: str
    description: str
    icon_code: str
    wind: WindInfo
    sun: SunTimes
    metrics: AtmosphericMetrics
    timezone_offset: int
    local_time_str: str
    local_date_str: str
    fetched_at_str: str
    forecast: List[ForecastDay] = field(default_factory=list)

    @property
    def city_name(self) -> str:
        return self.location.name

    @property
    def country(self) -> str:
        return self.location.country

    @property
    def location_display(self) -> str:
        return self.location.display_name

    @property
    def formatted_temp(self) -> str:
        return f"{round(self.temp)}°C"

    @property
    def formatted_feels_like(self) -> str:
        return f"Feels like {round(self.feels_like)}°C"

    @property
    def formatted_high_low(self) -> str:
        return f"High {round(self.temp_max)}°   Low {round(self.temp_min)}°"

    @property
    def is_day(self) -> bool:
        return self.sun.is_day
