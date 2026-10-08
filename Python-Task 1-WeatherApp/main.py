"""Atmos — Weather Desk

Entrypoint script for the desktop weather workstation application.
"""

import sys
import tkinter as tk

from weather_app.ui.app import WeatherApp
from weather_app.core.weather_service import WeatherService
from weather_app.core.api import OpenWeatherAPI
from weather_app.core.config import load_app_config


def enable_windows_high_dpi() -> None:
    """Enable high DPI awareness on Windows to prevent blurry GUI rendering."""
    if sys.platform == "win32":
        try:
            import ctypes
            # Shcore DPI awareness: 1 = Process_System_DPI_Aware, 2 = Process_Per_Monitor_DPI_Aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main() -> None:
    """Initialize application environment, configure service layer, and start GUI loop."""
    # Robustly load environment variables from project root .env
    load_app_config()

    # Enable high-DPI scaling
    enable_windows_high_dpi()

    # Initialize root Tkinter window
    root = tk.Tk()

    # Create service and API client
    api_client = OpenWeatherAPI()
    weather_service = WeatherService(api=api_client)

    # Launch desktop application
    app = WeatherApp(root, service=weather_service)

    # Start main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
