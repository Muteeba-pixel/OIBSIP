"""Utility functions for meteorological conversions, formatting, calculations, and location data."""

import time
import math
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict, List, Tuple
from .models import Location


CARDINAL_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]

# Country name aliases for intelligent country-level location routing
COUNTRY_ALIASES = {
    "pk": "pakistan",
    "pak": "pakistan",
    "pakistan": "pakistan",
    "us": "united states",
    "usa": "united states",
    "united states": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "united kingdom": "united kingdom",
    "gb": "united kingdom",
    "britain": "united kingdom",
    "england": "united kingdom",
    "uae": "united arab emirates",
    "united arab emirates": "united arab emirates",
    "dubai": "united arab emirates",
    "jp": "japan",
    "japan": "japan",
    "fr": "france",
    "france": "france",
    "de": "germany",
    "germany": "germany",
    "ca": "canada",
    "canada": "canada",
    "au": "australia",
    "australia": "australia",
    "in": "india",
    "india": "india",
    "cn": "china",
    "china": "china",
    "sa": "saudi arabia",
    "saudi arabia": "saudi arabia",
    "tr": "turkey",
    "turkey": "turkey",
    "eg": "egypt",
    "egypt": "egypt",
    "br": "brazil",
    "brazil": "brazil",
    "it": "italy",
    "italy": "italy",
    "es": "spain",
    "spain": "spain",
    "ru": "russia",
    "russia": "russia",
    "sg": "singapore",
    "singapore": "singapore",
    "my": "malaysia",
    "malaysia": "malaysia",
    "id": "indonesia",
    "indonesia": "indonesia"
}

# Major locations for country queries
COUNTRY_MAJOR_LOCATIONS: Dict[str, List[Location]] = {
    "pakistan": [
        Location("Islamabad", 33.6844, 73.0479, "PK", "Islamabad Capital Territory"),
        Location("Lahore", 31.5204, 74.3587, "PK", "Punjab"),
        Location("Karachi", 24.8607, 67.0011, "PK", "Sindh"),
        Location("Peshawar", 34.0151, 71.5249, "PK", "Khyber Pakhtunkhwa"),
        Location("Rawalpindi", 33.5651, 73.0169, "PK", "Punjab"),
        Location("Faisalabad", 31.4504, 73.1350, "PK", "Punjab"),
        Location("Multan", 30.1575, 71.5249, "PK", "Punjab"),
        Location("Quetta", 30.1798, 66.9750, "PK", "Balochistan"),
    ],
    "united states": [
        Location("New York", 40.7128, -74.0060, "US", "New York"),
        Location("Los Angeles", 34.0522, -118.2437, "US", "California"),
        Location("Chicago", 41.8781, -87.6298, "US", "Illinois"),
        Location("Houston", 29.7604, -95.3698, "US", "Texas"),
        Location("Phoenix", 33.4484, -112.0740, "US", "Arizona"),
        Location("San Francisco", 37.7749, -122.4194, "US", "California"),
        Location("Seattle", 47.6062, -122.3321, "US", "Washington"),
        Location("Miami", 25.7617, -80.1918, "US", "Florida"),
    ],
    "united kingdom": [
        Location("London", 51.5074, -0.1278, "GB", "England"),
        Location("Manchester", 53.4808, -2.2426, "GB", "England"),
        Location("Birmingham", 52.4862, -1.8904, "GB", "England"),
        Location("Edinburgh", 55.9533, -3.1883, "GB", "Scotland"),
        Location("Glasgow", 55.8642, -4.2518, "GB", "Scotland"),
        Location("Liverpool", 53.4084, -2.9916, "GB", "England"),
    ],
    "japan": [
        Location("Tokyo", 35.6762, 139.6503, "JP", "Tokyo"),
        Location("Osaka", 34.6937, 135.5023, "JP", "Osaka"),
        Location("Kyoto", 35.0116, 135.7681, "JP", "Kyoto"),
        Location("Yokohama", 35.4437, 139.6380, "JP", "Kanagawa"),
        Location("Sapporo", 43.0618, 141.3545, "JP", "Hokkaido"),
        Location("Fukuoka", 33.5904, 130.4017, "JP", "Fukuoka"),
    ],
    "united arab emirates": [
        Location("Dubai", 25.2048, 55.2708, "AE", "Dubai"),
        Location("Abu Dhabi", 24.4539, 54.3773, "AE", "Abu Dhabi"),
        Location("Sharjah", 25.3463, 55.4209, "AE", "Sharjah"),
        Location("Ajman", 25.4052, 55.5136, "AE", "Ajman"),
        Location("Ras Al Khaimah", 25.7895, 55.9432, "AE", "Ras Al Khaimah"),
    ],
    "france": [
        Location("Paris", 48.8566, 2.3522, "FR", "Île-de-France"),
        Location("Marseille", 43.2965, 5.3698, "FR", "Provence-Alpes-Côte d'Azur"),
        Location("Lyon", 45.7640, 4.8357, "FR", "Auvergne-Rhône-Alpes"),
        Location("Toulouse", 43.6047, 1.4442, "FR", "Occitanie"),
        Location("Nice", 43.7102, 7.2620, "FR", "Provence-Alpes-Côte d'Azur"),
    ],
    "germany": [
        Location("Berlin", 52.5200, 13.4050, "DE", "Berlin"),
        Location("Munich", 48.1351, 11.5820, "DE", "Bavaria"),
        Location("Frankfurt", 50.1109, 8.6821, "DE", "Hesse"),
        Location("Hamburg", 53.5511, 9.9937, "DE", "Hamburg"),
        Location("Cologne", 50.9375, 6.9603, "DE", "North Rhine-Westphalia"),
    ],
    "canada": [
        Location("Toronto", 43.6532, -79.3832, "CA", "Ontario"),
        Location("Vancouver", 49.2827, -123.1207, "CA", "British Columbia"),
        Location("Montreal", 45.5017, -73.5673, "CA", "Quebec"),
        Location("Calgary", 51.0447, -114.0719, "CA", "Alberta"),
        Location("Ottawa", 45.4215, -75.6972, "CA", "Ontario"),
    ],
    "australia": [
        Location("Sydney", -33.8688, 151.2093, "AU", "New South Wales"),
        Location("Melbourne", -37.8136, 144.9631, "AU", "Victoria"),
        Location("Brisbane", -27.4698, 153.0251, "AU", "Queensland"),
        Location("Perth", -31.9505, 115.8605, "AU", "Western Australia"),
        Location("Adelaide", -34.9285, 138.6007, "AU", "South Australia"),
    ],
    "china": [
        Location("Beijing", 39.9042, 116.4074, "CN", "Beijing"),
        Location("Shanghai", 31.2304, 121.4737, "CN", "Shanghai"),
        Location("Guangzhou", 23.1291, 113.2644, "CN", "Guangdong"),
        Location("Shenzhen", 22.5431, 114.0579, "CN", "Guangdong"),
    ],
    "india": [
        Location("New Delhi", 28.6139, 77.2090, "IN", "Delhi"),
        Location("Mumbai", 19.0760, 72.8777, "IN", "Maharashtra"),
        Location("Bengaluru", 12.9716, 77.5946, "IN", "Karnataka"),
        Location("Kolkata", 22.5726, 88.3639, "IN", "West Bengal"),
        Location("Chennai", 13.0827, 80.2707, "IN", "Tamil Nadu"),
    ],
    "saudi arabia": [
        Location("Riyadh", 24.7136, 46.6753, "SA", "Riyadh Province"),
        Location("Jeddah", 21.4858, 39.1925, "SA", "Makkah Province"),
        Location("Mecca", 21.3891, 39.8579, "SA", "Makkah Province"),
        Location("Medina", 24.5247, 39.5692, "SA", "Al Madinah Province"),
    ],
    "turkey": [
        Location("Istanbul", 41.0082, 28.9784, "TR", "Istanbul"),
        Location("Ankara", 39.9334, 32.8597, "TR", "Ankara"),
        Location("Izmir", 38.4237, 27.1428, "TR", "Izmir"),
        Location("Antalya", 36.8969, 30.7133, "TR", "Antalya"),
    ],
    "egypt": [
        Location("Cairo", 30.0444, 31.2357, "EG", "Cairo"),
        Location("Alexandria", 31.2001, 29.9187, "EG", "Alexandria"),
        Location("Giza", 30.0131, 31.2089, "EG", "Giza"),
    ],
    "brazil": [
        Location("São Paulo", -23.5505, -46.6333, "BR", "São Paulo"),
        Location("Rio de Janeiro", -22.9068, -43.1729, "BR", "Rio de Janeiro"),
        Location("Brasília", -15.8267, -47.9218, "BR", "Federal District"),
    ],
    "italy": [
        Location("Rome", 41.9028, 12.4964, "IT", "Lazio"),
        Location("Milan", 45.4642, 9.1900, "IT", "Lombardy"),
        Location("Naples", 40.8518, 14.2681, "IT", "Campania"),
        Location("Florence", 43.7696, 11.2558, "IT", "Tuscany"),
        Location("Venice", 45.4408, 12.3155, "IT", "Veneto"),
    ],
    "spain": [
        Location("Madrid", 40.4168, -3.7038, "ES", "Community of Madrid"),
        Location("Barcelona", 41.3851, 2.1734, "ES", "Catalonia"),
        Location("Valencia", 39.4699, -0.3763, "ES", "Valencian Community"),
        Location("Seville", 37.3891, -5.9845, "ES", "Andalusia"),
    ],
    "singapore": [
        Location("Singapore", 1.3521, 103.8198, "SG", "Central Region")
    ]
}

# Offline Global Cities Index to ensure immediate high-precision suggestions
OFFLINE_WORLD_LOCATIONS: List[Location] = []
# Pre-populate from COUNTRY_MAJOR_LOCATIONS
for _loc_list in COUNTRY_MAJOR_LOCATIONS.values():
    OFFLINE_WORLD_LOCATIONS.extend(_loc_list)

# Additional global hubs
OFFLINE_WORLD_LOCATIONS.extend([
    Location("Amsterdam", 52.3676, 4.9041, "NL", "North Holland"),
    Location("Bangkok", 13.7563, 100.5018, "TH", "Bangkok"),
    Location("Barcelona", 41.3851, 2.1734, "ES", "Catalonia"),
    Location("Brussels", 50.8503, 4.3517, "BE", "Brussels"),
    Location("Buenos Aires", -34.6037, -58.3816, "AR", "Buenos Aires"),
    Location("Cape Town", -33.9249, 18.4241, "ZA", "Western Cape"),
    Location("Copenhagen", 55.6761, 12.5683, "DK", "Capital Region"),
    Location("Doha", 25.2854, 51.5310, "QA", "Ad Dawhah"),
    Location("Dublin", 53.3498, -6.2603, "IE", "Leinster"),
    Location("Helsinki", 60.1699, 24.9384, "FI", "Uusimaa"),
    Location("Hong Kong", 22.3193, 114.1694, "HK", "Hong Kong"),
    Location("Jakarta", -6.2088, 106.8456, "ID", "Jakarta"),
    Location("Johannesburg", -26.2041, 28.0473, "ZA", "Gauteng"),
    Location("Kuala Lumpur", 3.1390, 101.6869, "MY", "Federal Territory"),
    Location("Kuwait City", 29.3759, 47.9774, "KW", "Al Asimah"),
    Location("Lisbon", 38.7223, -9.1393, "PT", "Lisbon"),
    Location("London", 42.9849, -81.2453, "CA", "Ontario"),  # Canadian London
    Location("Manila", 14.5995, 120.9842, "PH", "Metro Manila"),
    Location("Mexico City", 19.4326, -99.1332, "MX", "CDMX"),
    Location("Muscat", 23.5859, 58.4059, "OM", "Muscat"),
    Location("Nairobi", -1.2921, 36.8219, "KE", "Nairobi"),
    Location("Oslo", 59.9139, 10.7522, "NO", "Oslo"),
    Location("Prague", 50.0755, 14.4378, "CZ", "Prague"),
    Location("Reykjavik", 64.1466, -21.9426, "IS", "Capital Region"),
    Location("Santiago", -33.4489, -70.6693, "CL", "Santiago Metropolitan"),
    Location("Seoul", 37.5665, 126.9780, "KR", "Seoul"),
    Location("Stockholm", 59.3293, 18.0686, "SE", "Stockholm"),
    Location("Taipei", 25.0330, 121.5654, "TW", "Taipei"),
    Location("Vienna", 48.2082, 16.3738, "AT", "Vienna"),
    Location("Warsaw", 52.2297, 21.0122, "PL", "Masovia"),
    Location("Zurich", 47.3769, 8.5417, "CH", "Zurich")
])


def search_country_locations(query: str) -> Optional[List[Location]]:
    """
    If the query represents a country name or alias, return its major locations.
    E.g. 'pakistan' -> [Islamabad, Lahore, Karachi, Peshawar, ...]
    """
    clean = query.strip().lower()
    canonical_country = COUNTRY_ALIASES.get(clean)
    if canonical_country and canonical_country in COUNTRY_MAJOR_LOCATIONS:
        return COUNTRY_MAJOR_LOCATIONS[canonical_country]
    return None


def search_offline_locations(query: str, limit: int = 7) -> List[Location]:
    """
    Filter offline locations by prefix or substring match for instant suggestions.
    """
    clean = query.strip().lower()
    if not clean:
        return []

    # 1. Check country-level match first
    country_match = search_country_locations(clean)
    if country_match:
        return country_match[:limit]

    # 2. Search city names starting with query
    prefix_matches = [loc for loc in OFFLINE_WORLD_LOCATIONS if loc.name.lower().startswith(clean)]

    # 3. Search substring in city, state, or country
    sub_matches = [
        loc for loc in OFFLINE_WORLD_LOCATIONS
        if loc not in prefix_matches and (
            clean in loc.name.lower() or
            (loc.state and clean in loc.state.lower()) or
            clean in loc.country_full_name.lower()
        )
    ]

    combined = prefix_matches + sub_matches
    # Deduplicate while preserving order
    seen = set()
    result = []
    for loc in combined:
        key = (loc.name, loc.state, loc.country)
        if key not in seen:
            seen.add(key)
            result.append(loc)

    return result[:limit]


# -------------------------------------------------------------
# Meteorological Helpers
# -------------------------------------------------------------

def deg_to_compass(deg: float) -> str:
    """Convert wind azimuth degrees (0-360) to a 16-point cardinal compass direction."""
    normalized = float(deg) % 360
    val = int((normalized / 22.5) + 0.5)
    return CARDINAL_DIRECTIONS[val % 16]


def ms_to_kmh(speed_ms: float) -> float:
    """Convert velocity from meters per second to kilometers per hour."""
    return round(float(speed_ms) * 3.6, 1)


def wind_beaufort_description(speed_kmh: float) -> str:
    """Return Beaufort scale classification description for wind velocity in km/h."""
    if speed_kmh < 2:
        return "Calm"
    elif speed_kmh < 6:
        return "Light air"
    elif speed_kmh < 12:
        return "Light breeze"
    elif speed_kmh < 20:
        return "Gentle breeze"
    elif speed_kmh < 29:
        return "Moderate breeze"
    elif speed_kmh < 39:
        return "Fresh breeze"
    elif speed_kmh < 50:
        return "Strong breeze"
    elif speed_kmh < 62:
        return "High wind"
    elif speed_kmh < 75:
        return "Gale"
    else:
        return "Severe storm"


def calculate_dew_point(temp_c: float, humidity_pct: float) -> float:
    """Calculate approximate dew point in Celsius using the Magnus formula."""
    if humidity_pct <= 0:
        return temp_c
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_pct / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 1)


def humidity_comfort_level(humidity_pct: int) -> str:
    """Provide human-readable humidity comfort classification."""
    if humidity_pct < 30:
        return "Dry air"
    elif humidity_pct <= 60:
        return "Comfortable"
    elif humidity_pct <= 75:
        return "Moderately humid"
    else:
        return "High humidity"


def pressure_level_description(pressure_hpa: int) -> str:
    """Provide barometric pressure tendency description."""
    if pressure_hpa < 1005:
        return "Low pressure system"
    elif pressure_hpa <= 1022:
        return "Normal atmospheric level"
    else:
        return "High pressure system"


def visibility_description(visibility_km: float) -> str:
    """Provide qualitative visibility description."""
    if visibility_km >= 10:
        return "Clear horizon"
    elif visibility_km >= 4:
        return "Good visibility"
    elif visibility_km > 1:
        return "Moderate haze"
    else:
        return "Dense fog / mist"


def cloud_coverage_description(clouds_pct: int) -> str:
    """Provide cloud coverage description."""
    if clouds_pct <= 10:
        return "Clear sky"
    elif clouds_pct <= 30:
        return "Mostly sunny"
    elif clouds_pct <= 60:
        return "Partly cloudy"
    elif clouds_pct <= 85:
        return "Mostly cloudy"
    else:
        return "Overcast"


def timestamp_to_local_datetime(unix_ts: int, tz_offset_seconds: int) -> datetime:
    """Convert Unix timestamp and timezone offset in seconds to a local datetime."""
    tz = timezone(timedelta(seconds=tz_offset_seconds))
    return datetime.fromtimestamp(unix_ts, tz=tz)


def format_local_time(unix_ts: int, tz_offset_seconds: int, fmt: str = "%I:%M %p") -> str:
    """Format Unix timestamp as a 12-hour local time string (e.g., '06:45 AM')."""
    dt = timestamp_to_local_datetime(unix_ts, tz_offset_seconds)
    formatted = dt.strftime(fmt)
    if formatted.startswith("0") and ("%I" in fmt or "%d" in fmt):
        formatted = formatted.lstrip("0")
    return formatted


def format_local_date(unix_ts: int, tz_offset_seconds: int) -> str:
    """Format Unix timestamp as a readable local date (e.g., 'Tuesday, October 6')."""
    dt = timestamp_to_local_datetime(unix_ts, tz_offset_seconds)
    return dt.strftime("%A, %B %d")


def calculate_daylight_duration(sunrise_ts: int, sunset_ts: int) -> str:
    """Calculate the daylight duration string (e.g., '12h 35m') between sunrise and sunset."""
    seconds = max(0, sunset_ts - sunrise_ts)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes:02d}m"


def is_daytime(current_unix: int, sunrise_unix: int, sunset_unix: int) -> bool:
    """Determine whether the given current timestamp is between sunrise and sunset."""
    if sunrise_unix <= 0 or sunset_unix <= 0:
        return True
    return sunrise_unix <= current_unix <= sunset_unix


def calculate_solar_progress(current_unix: int, sunrise_unix: int, sunset_unix: int) -> float:
    """
    Calculate fraction of daylight elapsed (0.0 to 1.0).
    Returns -1.0 if currently nighttime.
    """
    if sunrise_unix <= 0 or sunset_unix <= 0 or sunset_unix <= sunrise_unix:
        return 0.5
    if current_unix < sunrise_unix:
        return -1.0
    if current_unix > sunset_unix:
        return -1.0
    return max(0.0, min(1.0, (current_unix - sunrise_unix) / float(sunset_unix - sunrise_unix)))


def format_condition_title(description: str) -> str:
    """Format weather description into title case (e.g. 'scattered clouds' -> 'Scattered Clouds')."""
    if not description:
        return "Unknown"
    return " ".join(word.capitalize() for word in description.strip().split())


class CacheItem:
    """Container for cached entry with expiration timestamp."""
    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


class WeatherCache:
    """Lightweight in-memory cache with time-to-live expiration."""
    def __init__(self, default_ttl_seconds: int = 300):
        self._default_ttl = default_ttl_seconds
        self._store: Dict[str, CacheItem] = {}

    def _normalize_key(self, key: str) -> str:
        return key.strip().lower()

    def get(self, key: str) -> Optional[Any]:
        norm_key = self._normalize_key(key)
        item = self._store.get(norm_key)
        if item and item.is_valid():
            return item.data
        if item:
            del self._store[norm_key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        norm_key = self._normalize_key(key)
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._store[norm_key] = CacheItem(value, ttl)

    def invalidate(self, key: str) -> None:
        norm_key = self._normalize_key(key)
        if norm_key in self._store:
            del self._store[norm_key]

    def clear(self) -> None:
        self._store.clear()
