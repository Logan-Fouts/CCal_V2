import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from weather_tracker import WeatherTracker

import pytest
import time
from unittest.mock import patch, MagicMock

# Mock data for testing
data = {
    "weather": [{"main": "Rain"}],
    "main": {"temp": 15}
}

@pytest.fixture
def tracker():
    return WeatherTracker("dummy_api_key", lat=10.0, lon=20.0)

@pytest.fixture(autouse=True)
def run_before_each_test(tracker):
    tracker.update_weather("current", data)

def test_update_weather_sets_cache(tracker):
    assert tracker.cached_weather == "rain"
    assert tracker.weather_data["current"] == data
    assert abs(tracker.last_update_time - time.time()) < 2

def test_get_weather(tracker):
    result = tracker.get_weather()
    assert result["condition"] == "rain"
    assert result["temperature"] == 15

def test_make_weather_request_success(monkeypatch, tracker):
    mock_response = MagicMock()
    mock_response.json.return_value = {"weather": [{"main": "Clouds"}], "main": {"temp": 20}}
    mock_response.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *a, **kw: mock_response)
    result = tracker._make_weather_request()
    assert result["weather"][0]["main"] == "Clouds"
    assert result["main"]["temp"] == 20

def test_make_weather_request_failure(monkeypatch, tracker):
    def raise_exc(*a, **kw):
        raise Exception("Network error")
    monkeypatch.setattr("requests.get", raise_exc)
    result = tracker._make_weather_request(max_retries=1)
    assert result is None

def test_get_weather_api(monkeypatch, tracker):
    # Invalidate cache
    tracker.last_update_time = 0
    mock_data = {"weather": [{"main": "Clear"}], "main": {"temp": 22}}
    monkeypatch.setattr(tracker, "_make_weather_request", lambda: mock_data)
    result = tracker.get_weather()
    assert result["condition"] == "clear"
    assert result["temperature"] == 22

def test_get_weather_stale_cache(tracker):
    # Simulate stale cache by setting last_update_time far in the past 
    tracker.last_update_time = time.time() - 99999
    tracker.cached_weather = "clouds"
    tracker.weather_data["current"] = {"main": {"temp": 10}}
    # Patch _make_weather_request to return None
    tracker._make_weather_request = lambda *a, **kw: None
    result = tracker.get_weather()
    assert result["condition"] == "clouds"
    assert result["temperature"] == 10

def test_get_weather_default(tracker):
    # Remove cache and patch _make_weather_request to return None
    tracker.cached_weather = None
    tracker.weather_data = {}
    tracker._make_weather_request = lambda *a, **kw: None
    result = tracker.get_weather()
    assert result["condition"] == "clear"
    assert result["temperature"] is None

def test_update_weather_sets_cache(tracker):
    assert tracker.cached_weather == "rain"
    assert tracker.weather_data["current"] == data
    assert abs(tracker.last_update_time - time.time()) < 2

def test_get_weather(tracker):
    result = tracker.get_weather()
    assert result["condition"] == "rain"
    assert result["temperature"] == 15