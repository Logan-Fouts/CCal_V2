"""
WeatherTracker integration module.

Provides the WeatherTracker class for retrieving and caching current weather data
from the OpenWeatherMap API for a specified location.

Features:
- Fetches weather data using an API key and geographic coordinates
- Caches results for a configurable duration to minimize API calls
- Handles network errors and retries failed requests
- Designed for integration with LED control and other systems
"""

import time
import requests


class WeatherTracker:
    """
    Tracks and caches current weather data for a specified
    location using the OpenWeatherMap API.

    Usage:
        wt = WeatherTracker(api_key, location)
        weather = wt.get_current_weather()
    """

    def __init__(self, api_key, location):
        self._location = location
        self._url = "https://api.openweathermap.org/data/3.0/onecall?lat={LOC[0]}&lon={LOC[1]}&appid={KEY}".format(
            LOC=location, KEY=api_key
        )
        self._current_weather = None
        self._cache_duration = 5 * 60  # 5 minutes
        self._cache_time = None

    def get_location(self):
        """Returns the location."""
        return self._location

    def _cache_expired(self):
        """Checks if the cached data has expired."""
        if self._cache_time is None:
            return True
        return (time.time() - self._cache_time) > self._cache_duration

    # Really the only method that should be used externally
    def get_current_weather(self):
        """Returns the current weather, updating if necessary."""
        if self._current_weather is None or self._cache_expired():
            weather = self._update_weather()
            return weather
        return self._current_weather

    def _update_weather(self):
        """Fetches the current weather from the API."""
        retries = 3
        timeout = 5
        for _ in range(retries):
            try:
                response = requests.get(self._url, timeout=timeout)
                if response.status_code == 200:
                    self._current_weather = response.json()
                    self._cache_time = time.time()
                    return self._current_weather
            except Exception:
                continue
        return self._current_weather
