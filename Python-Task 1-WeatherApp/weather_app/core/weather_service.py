"""Weather service handling business logic, location geocoding, caching, and forecast aggregation."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import collections

from .api import OpenWeatherAPI, CityNotFoundError
from .models import (
    Location,
    WeatherData,
    ForecastDay,
    WindInfo,
    SunTimes,
    AtmosphericMetrics,
)
from .utils import (
    WeatherCache,
    deg_to_compass,
    ms_to_kmh,
    wind_beaufort_description,
    calculate_dew_point,
    humidity_comfort_level,
    pressure_level_description,
    visibility_description,
    cloud_coverage_description,
    format_local_time,
    format_local_date,
    calculate_daylight_duration,
    calculate_solar_progress,
    is_daytime,
    format_condition_title,
    timestamp_to_local_datetime,
    search_country_locations,
    search_offline_locations,
)


class WeatherService:
    """High-level service coordinating geocoding, weather fetching, caching, and normalization."""

    def __init__(self, api: Optional[OpenWeatherAPI] = None, cache: Optional[WeatherCache] = None):
        self.api = api or OpenWeatherAPI()
        self.cache = cache or WeatherCache(default_ttl_seconds=300)

    def search_locations(self, query: str, limit: int = 6) -> List[Location]:
        """
        Search for real global locations by query string.
        Supports country search, city names worldwide, and prefix typing.
        
        Returns:
            List of Location models with exact coordinates.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Country-level query check (e.g. 'Pakistan', 'USA', 'Japan', 'UK')
        country_match = search_country_locations(clean_query)
        if country_match:
            return country_match[:limit]

        # 2. Try OpenWeatherMap Geocoding API if key configured
        if self.api.has_api_key:
            try:
                raw_items = self.api.search_locations(clean_query, limit=limit)
                if raw_items:
                    locations = []
                    seen = set()
                    for item in raw_items:
                        loc = Location(
                            name=item.get("name", clean_query),
                            lat=float(item.get("lat", 0.0)),
                            lon=float(item.get("lon", 0.0)),
                            country=item.get("country", ""),
                            state=item.get("state")
                        )
                        key = (loc.name.lower(), (loc.state or "").lower(), loc.country.lower())
                        if key not in seen:
                            seen.add(key)
                            locations.append(loc)
                    if locations:
                        return locations[:limit]
            except Exception:
                pass

        # 3. Offline Global Cities fallback
        return search_offline_locations(clean_query, limit=limit)

    def fetch_weather_by_location(self, location: Location, force_refresh: bool = False) -> WeatherData:
        """
        Fetch real-time weather and forecast using exact coordinates.
        """
        cache_key = f"{round(location.lat, 3)}_{round(location.lon, 3)}"

        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        # Fetch live data using coordinates
        current_raw = self.api.get_current_weather_by_coords(location.lat, location.lon)
        forecast_raw = self.api.get_forecast_by_coords(location.lat, location.lon)

        weather_data = self._build_weather_data(location, current_raw, forecast_raw)
        self.cache.set(cache_key, weather_data)
        return weather_data

    def fetch_weather(self, city: str, force_refresh: bool = False) -> WeatherData:
        """
        Retrieve weather for a query string by resolving location first, then using exact coordinates.
        """
        clean = city.strip()
        if not clean:
            raise ValueError("City name must not be empty.")

        locations = self.search_locations(clean, limit=1)
        if not locations:
            # Fall back to direct city name query if geocoder returned no matches
            current_raw = self.api.get_current_weather(clean)
            forecast_raw = self.api.get_forecast(clean)
            coord = current_raw.get("coord", {})
            loc = Location(
                name=current_raw.get("name", clean),
                lat=coord.get("lat", 0.0),
                lon=coord.get("lon", 0.0),
                country=current_raw.get("sys", {}).get("country", "")
            )
            return self._build_weather_data(loc, current_raw, forecast_raw)

        return self.fetch_weather_by_location(locations[0], force_refresh=force_refresh)

    def _build_weather_data(
        self,
        location: Location,
        current: Dict[str, Any],
        forecast_json: Dict[str, Any]
    ) -> WeatherData:
        """Parse raw JSON payloads into strongly-typed WeatherData."""
        sys_data = current.get("sys", {})
        # If location model has country code, ensure it aligns
        country = location.country or sys_data.get("country", "")

        main_data = current.get("main", {})
        temp = float(main_data.get("temp", 0.0))
        feels_like = float(main_data.get("feels_like", temp))
        temp_min = float(main_data.get("temp_min", temp))
        temp_max = float(main_data.get("temp_max", temp))
        humidity = int(main_data.get("humidity", 0))
        pressure = int(main_data.get("pressure", 1013))

        weather_list = current.get("weather", [])
        weather_primary = weather_list[0] if weather_list else {}
        condition = weather_primary.get("main", "Clear")
        description = format_condition_title(weather_primary.get("description", "Clear sky"))
        icon_code = weather_primary.get("icon", "01d")

        # Wind
        wind_data = current.get("wind", {})
        wind_speed_ms = float(wind_data.get("speed", 0.0))
        wind_deg = int(wind_data.get("deg", 0))
        gust_ms = wind_data.get("gust")
        gust_kmh = ms_to_kmh(gust_ms) if gust_ms is not None else None
        speed_kmh = ms_to_kmh(wind_speed_ms)

        wind_info = WindInfo(
            speed_kmh=speed_kmh,
            deg=wind_deg,
            direction=deg_to_compass(wind_deg),
            gust_kmh=gust_kmh,
            beaufort_desc=wind_beaufort_description(speed_kmh)
        )

        # Time and Solar Cycle
        tz_offset = int(current.get("timezone", 0))
        current_unix = int(current.get("dt", int(datetime.now(timezone.utc).timestamp())))
        sunrise_unix = int(sys_data.get("sunrise", 0))
        sunset_unix = int(sys_data.get("sunset", 0))

        sunrise_local = format_local_time(sunrise_unix, tz_offset) if sunrise_unix else "--:--"
        sunset_local = format_local_time(sunset_unix, tz_offset) if sunset_unix else "--:--"
        daylight_duration = calculate_daylight_duration(sunrise_unix, sunset_unix) if sunrise_unix and sunset_unix else "--"
        is_day = is_daytime(current_unix, sunrise_unix, sunset_unix)
        solar_progress = calculate_solar_progress(current_unix, sunrise_unix, sunset_unix)

        sun_times = SunTimes(
            sunrise_unix=sunrise_unix,
            sunset_unix=sunset_unix,
            sunrise_local=sunrise_local,
            sunset_local=sunset_local,
            daylight_duration=daylight_duration,
            is_day=is_day,
            solar_progress=solar_progress
        )

        # Atmosphere
        visibility_meters = current.get("visibility", 10000)
        visibility_km = round(visibility_meters / 1000.0, 1)
        cloud_all = int(current.get("clouds", {}).get("all", 0))
        dew_point_c = calculate_dew_point(temp, humidity)

        metrics = AtmosphericMetrics(
            humidity=humidity,
            pressure=pressure,
            visibility_km=visibility_km,
            cloudiness=cloud_all,
            dew_point_c=dew_point_c,
            humidity_status=humidity_comfort_level(humidity),
            pressure_status=pressure_level_description(pressure),
            visibility_status=visibility_description(visibility_km),
            cloud_status=cloud_coverage_description(cloud_all)
        )

        local_time_str = format_local_time(current_unix, tz_offset)
        local_date_str = format_local_date(current_unix, tz_offset)
        fetched_at_str = datetime.now().strftime("%I:%M %p").lstrip("0")

        forecast_days = self._aggregate_forecast(forecast_json.get("list", []), tz_offset, current_unix)

        if forecast_days and round(temp_min) == round(temp_max):
            today_forecast = forecast_days[0]
            temp_max = max(temp_max, today_forecast.temp_max)
            temp_min = min(temp_min, today_forecast.temp_min)

        return WeatherData(
            location=location,
            temp=temp,
            feels_like=feels_like,
            temp_min=temp_min,
            temp_max=temp_max,
            condition=condition,
            description=description,
            icon_code=icon_code,
            wind=wind_info,
            sun=sun_times,
            metrics=metrics,
            timezone_offset=tz_offset,
            local_time_str=local_time_str,
            local_date_str=local_date_str,
            fetched_at_str=fetched_at_str,
            forecast=forecast_days
        )

    def _aggregate_forecast(
        self,
        raw_items: List[Dict[str, Any]],
        tz_offset: int,
        current_unix: int
    ) -> List[ForecastDay]:
        """Group 3-hour forecast entries into daily summaries."""
        if not raw_items:
            return []

        current_local_dt = timestamp_to_local_datetime(current_unix, tz_offset)
        current_local_date = current_local_dt.date()

        grouped: Dict[Any, List[Dict[str, Any]]] = collections.defaultdict(list)
        for item in raw_items:
            dt_unix = int(item.get("dt", 0))
            local_dt = timestamp_to_local_datetime(dt_unix, tz_offset)
            grouped[local_dt.date()].append(item)

        forecast_results: List[ForecastDay] = []

        for date_key in sorted(grouped.keys()):
            items = grouped[date_key]
            if not items:
                continue

            temps = [float(it.get("main", {}).get("temp", 0.0)) for it in items]
            temp_mins = [float(it.get("main", {}).get("temp_min", t)) for it, t in zip(items, temps)]
            temp_maxs = [float(it.get("main", {}).get("temp_max", t)) for it, t in zip(items, temps)]

            day_high = max(temp_maxs)
            day_low = min(temp_mins)

            pops = [float(it.get("pop", 0.0)) for it in items]
            max_pop_pct = int(round(max(pops) * 100)) if pops else 0

            humidities = [int(it.get("main", {}).get("humidity", 0)) for it in items]
            avg_humidity = int(sum(humidities) / len(humidities)) if humidities else 0

            wind_speeds = [ms_to_kmh(it.get("wind", {}).get("speed", 0.0)) for it in items]
            avg_wind = round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else 0.0

            best_item = self._find_midday_item(items, tz_offset)
            weather_list = best_item.get("weather", [])
            primary_weather = weather_list[0] if weather_list else {}
            condition = primary_weather.get("main", "Clear")
            description = format_condition_title(primary_weather.get("description", "Clear sky"))
            icon_code = primary_weather.get("icon", "01d")

            if date_key == current_local_date:
                day_name = "Today"
            else:
                day_name = date_key.strftime("%a")

            date_str = date_key.strftime("%b %d")

            forecast_results.append(
                ForecastDay(
                    date_str=date_str,
                    day_name=day_name,
                    condition=condition,
                    description=description,
                    icon_code=icon_code,
                    temp_max=day_high,
                    temp_min=day_low,
                    pop=max_pop_pct,
                    humidity_avg=avg_humidity,
                    wind_speed_avg=avg_wind
                )
            )

            if len(forecast_results) >= 5:
                break

        return forecast_results

    def _find_midday_item(self, items: List[Dict[str, Any]], tz_offset: int) -> Dict[str, Any]:
        """Find the forecast entry closest to 1:00 PM (13:00) local time for best daytime representation."""
        best_item = items[len(items) // 2]
        min_distance = float("inf")

        for item in items:
            dt_unix = int(item.get("dt", 0))
            local_dt = timestamp_to_local_datetime(dt_unix, tz_offset)
            hour_diff = abs(local_dt.hour - 13)
            if hour_diff < min_distance:
                min_distance = hour_diff
                best_item = item

        return best_item
