from unittest.mock import Mock, patch
from led_control.integrations.weather_tracker import WeatherTracker

API_KEY = "blahblah"
LOCATION = [40.7128, -74.0060]  # New York City coordinates
RESPONSE_JSON = {
    "current": {"weather": {"main": "Sunny"}, "temp": 72},
}


def test_initialize_with_args():
    """Test initializing WeatherTracker with arguments."""
    wt = WeatherTracker(API_KEY, LOCATION)
    assert wt.getLocation() == LOCATION


@patch("led_control.integrations.weather_tracker.requests.get")
def test_get_weather_makes_get_request(mock_get):
    """Test that updateWeather() makes a GET request to the correct endpoint."""
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.return_value = mock_response

    wt = WeatherTracker(API_KEY, LOCATION)

    weather = wt.updateWeather()

    mock_get.assert_called_once()

    expected_url = "https://api.openweathermap.org/data/3.0/onecall?lat={LOCATION[0]}&lon={LOCATION[1]}&appid={API_key}".format(
        LOCATION=LOCATION, API_key=API_KEY
    )

    assert weather is not None
    assert wt.getCurrentWeather() == RESPONSE_JSON
    assert weather == RESPONSE_JSON
