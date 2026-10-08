"""Unit tests for centralized configuration management in weather_app.core.config."""

from pathlib import Path
from weather_app.core.config import (
    get_project_root,
    load_app_config,
    get_openweather_api_key,
    has_openweather_api_key,
)


def test_get_project_root():
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()
    assert (root / "main.py").exists()
    assert (root / "weather_app").exists()


def test_load_app_config_idempotent():
    # Calling load_app_config multiple times should never raise exceptions
    load_app_config()
    load_app_config()


def test_get_openweather_api_key_type():
    key = get_openweather_api_key()
    assert isinstance(key, str)


def test_has_openweather_api_key_type():
    has_key = has_openweather_api_key()
    assert isinstance(has_key, bool)
