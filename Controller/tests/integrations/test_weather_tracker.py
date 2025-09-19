"""
Unit tests for the WeatherTracker integration module.

This test suite verifies the behavior of the WeatherTracker class, including:
- Initialization with API key and location
- Making GET requests to the weather API
- Handling request exceptions and retry logic
- Caching and cache expiration of weather data
- Ensuring correct use of mocked responses

Tests use unittest.mock to patch network calls and simulate various scenarios.
"""

import time
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
    assert wt.get_location() == LOCATION


@patch("led_control.integrations.weather_tracker.requests.get")
def test_get_weather_makes_get_request(mock_get):
    """Test that updateWeather() makes a GET request to the correct endpoint."""
    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.return_value = mock_response

    wt = WeatherTracker(API_KEY, LOCATION)

    weather = wt._update_weather()
    mock_get.assert_called_once()

    assert weather is not None
    assert wt.get_current_weather() == RESPONSE_JSON
    assert weather == RESPONSE_JSON


@patch("led_control.integrations.weather_tracker.requests.get")
def test_update_weather_handles_request_exception(mock_get):
    """Test that updateWeather() handles request exceptions gracefully."""
    mock_get.side_effect = Exception("Network error")

    wt = WeatherTracker(API_KEY, LOCATION)

    weather = wt._update_weather()

    assert weather is None
    assert wt.get_current_weather() is None


@patch("led_control.integrations.weather_tracker.requests.get")
def test_update_weather_retries_on_failure(mock_get):
    """Test that updateWeather() retries on failure."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.side_effect = [Exception("Network error"), Exception("Network error"), mock_response]

    wt = WeatherTracker(API_KEY, LOCATION)

    weather = wt._update_weather()

    assert weather == RESPONSE_JSON
    assert wt.get_current_weather() == RESPONSE_JSON
    assert mock_get.call_count == 3


@patch("led_control.integrations.weather_tracker.requests.get")
def test_update_weather_fails_after_max_retries(mock_get):
    """Test that updateWeather() returns None after max retries."""
    mock_get.side_effect = Exception("Network error")

    wt = WeatherTracker(API_KEY, LOCATION)

    weather = wt._update_weather()

    assert weather is None
    assert mock_get.call_count == 3


@patch("led_control.integrations.weather_tracker.requests.get")
def test_get_weather_uses_cached_data(mock_get):
    """Test that getCurrentWeather() returns cached data if within cache duration."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.return_value = mock_response

    wt = WeatherTracker(API_KEY, LOCATION)

    weather1 = wt.get_current_weather()
    wt._current_weather = "Modified Data"
    weather2 = wt.get_current_weather()

    assert weather1 == RESPONSE_JSON
    assert weather2 == "Modified Data"
    mock_get.assert_called_once()


@patch("led_control.integrations.weather_tracker.requests.get")
def test_get_weather_no_cache_initially(mock_get):
    """Test that getCurrentWeather() calls updateWeather() if no cached data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.return_value = mock_response

    wt = WeatherTracker(API_KEY, LOCATION)

    assert wt._current_weather is None
    weather = wt.get_current_weather()

    assert weather == RESPONSE_JSON
    assert wt.get_current_weather() == RESPONSE_JSON
    mock_get.assert_called_once()


@patch("led_control.integrations.weather_tracker.requests.get")
def test_get_weather_cache_expires(mock_get):
    """Test that getCurrentWeather() fetches new data after cache expires."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = RESPONSE_JSON
    mock_get.return_value = mock_response

    wt = WeatherTracker(API_KEY, LOCATION)
    wt._cache_duration = 1

    weather1 = wt.get_current_weather()
    wt._current_weather = "Modified Data"

    time.sleep(2)

    weather2 = wt.get_current_weather()

    assert weather1 == RESPONSE_JSON
    assert weather2 == RESPONSE_JSON
    assert mock_get.call_count == 2
