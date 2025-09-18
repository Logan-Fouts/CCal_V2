import requests

class WeatherTracker:
    def __init__(self, api_key, location):
        self._api_key = api_key
        self._location = location
        self._url = "https://api.openweathermap.org/data/3.0/onecall?lat={LOCATION[0]}&lon={LOCATION[1]}&appid={API_key}".format(
            LOCATION=location, API_key=api_key
        )
        self._current_weather = None

    def getLocation(self):
        return self._location

    def getCurrentWeather(self):
        # TODO: Implement caching so will update weather every X minutes
        return self._current_weather

    def updateWeather(self):
        try:
            response = requests.get(self._url)
            if response.status_code == 200:
                self._current_weather = response.json()
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
        return self._current_weather