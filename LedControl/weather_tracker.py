import time
import requests
from typing import Optional, Dict, Any


class WeatherTracker:
    """
    This class is used to track the weather conditions.
    It includes error handling, retry logic, and caching for reliability.
    """

    def __init__(self, API_KEY: str, lat: float = 40.71, lon: float = -74.01):
        self.weather_data: Dict[str, Any] = {}
        self.API_KEY = API_KEY
        self.lat = lat
        self.lon = lon
        self.last_update_time: float = 0
        self.cached_weather: Optional[str] = None
        self.CACHE_TIMEOUT = 1800  # 30 minutes in seconds 

    def _make_weather_request(self, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Internal method to make weather API request with retries.
        """
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.API_KEY}&units=metric"

        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(
                        f"Weather API request failed after {max_retries} attempts: {str(e)}"
                    )
                    return None
                time.sleep(2**attempt)

        return None

    def update_weather(self, location: str, data: Dict[str, Any]) -> None:
        """
        Update the weather data for a specific location.
        """
        self.weather_data[location] = data
        self.cached_weather = data.get("weather", [{}])[0].get("main", "").lower()
        self.last_update_time = time.time()

    def get_weather(self) -> Dict[str, Any]:
        """
        Retrieve the weather data, using cache if recent or API if available.
        Returns a dict with 'condition' and 'temperature'. Defaults to 'clear' and None if all methods fail.
        """
        current_time = time.time()

        if (
            self.cached_weather
            and (current_time - self.last_update_time) < self.CACHE_TIMEOUT
        ):
            print(f"Weather results (cached): {self.cached_weather}")
            # Try to get cached temperature if available
            temp = self.weather_data.get("current", {}).get("main", {}).get("temp")
            return {"condition": self.cached_weather, "temperature": temp}

        data = self._make_weather_request()

        if data:
            weather = data.get("weather", [{}])[0].get("main", "").lower()
            temp = data.get("main", {}).get("temp")
            print(f"Weather results: {weather}, Temp: {temp}")
            self.cached_weather = weather
            self.last_update_time = current_time
            self.weather_data["current"] = data
            return {"condition": weather, "temperature": temp}

        if self.cached_weather:
            print(f"Weather results (stale cache): {self.cached_weather}")
            temp = self.weather_data.get("current", {}).get("main", {}).get("temp")
            return {"condition": self.cached_weather, "temperature": temp}

        print("Weather results: unknown (using default)")
        return {"condition": "clear", "temperature": None}
