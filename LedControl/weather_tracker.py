import requests

class WEATHER_TRACKER:
    """
    This class is used to track the weather conditions.
    It is used to store and retrieve weather data.
    """

    def __init__(self, API_KEY=None, lat=40.71, lon=-74.01):
        self.weather_data = {}
        self.API_KEY = API_KEY
        self.lat = lat
        self.lon = lon

    def update_weather(self, location, data):
        """
        Update the weather data for a specific location.
        """
        self.weather_data[location] = data

    def get_weather(self):
        """
        Retrieve the weather data for a specific location.
        """
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.API_KEY}&units=metric"
        response = requests.get(url)
        print("Weather results: ", response.json()["weather"][0]["main"])
        return response.json()["weather"][0]["main"].lower()
