# Atmos — Weather Desk

Atmos Weather Desk is a desktop weather application built in Python and Tkinter for the OASIS Infobyte internship portfolio. It provides global location search with live autocomplete, exact coordinate-based weather retrieval, atmospheric measurements, solar cycle tracking, and a 5-day extended forecast powered by the OpenWeatherMap API.

The interface runs on a graphite and warm off-white design system with custom Tkinter Canvas vector graphics, an integrated dropdown suggestion menu, and background worker threads to keep the desktop interface responsive.

---

## Features

- **Global Location Search & Autocomplete**: Type any city or country worldwide. Real-time autocomplete suggestions display city name, state/region, and country.
- **Country Query Routing**: Searching for a country (e.g., "Pakistan", "United States", "Japan", "United Kingdom") returns its major metropolitan centres rather than treating an entire nation as a single point.
- **Exact Coordinate-Based Requests**: Selected locations resolve to exact latitude and longitude coordinates, which are passed directly to the OpenWeatherMap weather and forecast endpoints to prevent naming ambiguities.
- **Intentional Initial State**: The application launches into a finished welcome screen featuring a prominent search bar and quick-access chips for popular global locations. No empty placeholder boxes or missing metrics are displayed.
- **Current Weather Focus**: Displays current temperature (°C), weather condition, feels-like temperature, daily high/low range, and local date and time computed from the location's UTC timezone offset.
- **Atmospheric Conditions Grid**: Dedicated metric tiles for wind speed and direction (with Beaufort scale descriptor), relative humidity, calculated dew point, barometric pressure, horizontal visibility, and cloud cover.
- **Sun & Daylight Cycle**: Canvas-rendered celestial arc showing sunrise, sunset, total daylight duration, and the sun's trajectory position across the sky.
- **5-Day Extended Forecast**: Processed daily forecasts derived from 3-hour forecast intervals, showing the day of the week, date, weather icon, condition description, and temperature range.
- **Session Recent Searches**: Remembers up to 5 recently viewed locations during the active session for one-click switching.
- **Silent Developer Configuration**: API credentials are loaded silently from `.env` via `python-dotenv`. Normal users are never prompted with API key setup forms or textboxes.
- **Graceful Error Handling**: Dedicated technical status views for network connection failures, invalid locations, request timeouts, and unconfigured credentials.
- **Multi-Resolution Layout**: Designed to adapt cleanly across window resolutions from 1100x700 up to 1440x900 and beyond.

---

## Technologies Used

- **Python 3.10+**
- **Tkinter & ttk**: Standard desktop GUI toolkit
- **requests**: Network communication with OpenWeatherMap APIs
- **python-dotenv**: Environment variable parsing from `.env`
- **pytest**: Test suite with mocked responses

---

## Project Structure

```
Python-Task 1-WeatherApp/
│
├── weather_app/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api.py               # OpenWeatherMap client (geocoding, current weather, forecast)
│   │   ├── models.py            # Typed dataclasses (Location, WeatherData, ForecastDay, etc.)
│   │   ├── weather_service.py   # Coordinate resolution, caching, forecast aggregation
│   │   └── utils.py             # Meteorological calculations, unit conversions, offline index
│   │
│   └── ui/
│       ├── __init__.py
│       ├── app.py               # Application window controller and view state management
│       ├── components.py        # Autocomplete dropdown, search bar, metric tiles, forecast cards
│       ├── theme.py             # Color palette tokens, fonts, and day/night styles
│       └── icons.py             # Vector canvas weather symbols and solar arc widget
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py              # Geocoding and coordinate API client tests (mocked)
│   ├── test_models.py           # Location and weather data model tests
│   ├── test_ui.py               # GUI components, autocomplete dropdown, and theme tests
│   ├── test_utils.py            # Conversions, country searches, and cache tests
│   └── test_weather_service.py  # Service layer, coordinate fetching, and forecast aggregation tests
│
├── main.py                      # Application entry point with Windows high-DPI scaling
├── README.md                    # Project documentation
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore file (keeps .env untracked)
└── LICENSE                      # MIT License
```

---

## Getting Started

### 1. Prerequisites

Ensure Python 3.10 or newer is installed on your system.

### 2. Clone and Setup

```bash
cd "Python-Task 1-WeatherApp"
```

Optional: create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure API Credentials

The application uses the free OpenWeatherMap 2.5 API.

1. Obtain a free API key from [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Create a `.env` file in the project root by copying `.env.example`:
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env

   # Bash
   cp .env.example .env
   ```
3. Open `.env` and add your key:
   ```ini
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

*Note: The real `.env` file is excluded from Git by `.gitignore` to keep credentials secure.*

---

## Running the Application

Launch the desktop app with:

```bash
python main.py
```

### Keyboard Shortcuts

- `↑` / `↓` : Navigate autocomplete suggestions
- `Enter` : Select highlighted location or submit search query
- `Esc` : Close suggestions or return to the welcome screen
- `F5` : Refresh weather for the current location

---

## Running the Tests

Execute the automated test suite with `pytest`:

```bash
pytest -v
```

All 53 unit tests run with mocked HTTP responses and require no active internet connection or API key.

---

## Error Handling

Errors are caught cleanly by the service layer and displayed as clear status messages:

| Condition | Status Message |
|---|---|
| Location not found | `No matching locations found. Try another city or region.` |
| Unconfigured credentials | `Weather service unavailable. Weather API credentials are not configured in .env.` |
| Network offline | `Unable to connect to the weather service. Check your internet connection.` |
| Request timeout | `The weather service took too long to respond. Please try again.` |
| API rate limit / server error | `Weather service temporarily unavailable.` |

No Python tracebacks, raw JSON, or exception logs are presented to the user.

---

## Security Notes

- The API key is stored exclusively in `.env`, which is listed in `.gitignore` and never committed to source control.
- The key is not printed to the console or exposed in error messages.
- No user tracking or analytics are collected.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

