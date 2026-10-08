"""Centralized application configuration and robust .env loader.

Provides a single source of truth for loading environment settings,
resolving file paths relative to project root, and accessing the OpenWeather API key.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Project root is 3 levels up: weather_app/core/config.py -> Python-Task 1-WeatherApp/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


def load_app_config() -> None:
    """
    Reliably locate and load .env from the project root.
    Guarantees load_dotenv is executed before any service reads environment variables.
    """
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
    else:
        # Fallback to parent directory (e.g. when run from workspace root)
        parent_env = PROJECT_ROOT.parent / ".env"
        if parent_env.exists():
            load_dotenv(dotenv_path=parent_env, override=True)
        else:
            load_dotenv(override=True)


def get_openweather_api_key() -> str:
    """
    Retrieve the configured OPENWEATHER_API_KEY from environment.
    Automatically ensures .env is loaded first.
    Never logs or exposes the key value.
    """
    load_app_config()
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def has_openweather_api_key() -> bool:
    """Check whether a non-empty API key is configured."""
    return bool(get_openweather_api_key())
