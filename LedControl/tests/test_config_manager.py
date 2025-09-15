import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from weather_tracker import WEATHER_TRACKER
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
    return WEATHER_TRACKER("dummy_api_key", lat=10.0, lon=20.0)

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

import json
import tempfile
import pytest
from config_manager import CONFIG_MANAGER

def test_load_config_file_not_found(tmp_path):
    config_path = tmp_path / "missing.json"
    cm = CONFIG_MANAGER(str(config_path))
    config = cm.load_config()
    assert config == {}

def test_load_config_invalid_json(tmp_path):
    config_path = tmp_path / "bad.json"
    config_path.write_text("not a json")
    cm = CONFIG_MANAGER(str(config_path))
    config = cm.load_config()
    assert config == {}

def test_load_config_not_dict(tmp_path):
    config_path = tmp_path / "list.json"
    config_path.write_text(json.dumps([1,2,3]))
    cm = CONFIG_MANAGER(str(config_path))
    config = cm.load_config()
    assert config == {}

def test_load_config_valid(tmp_path):
    config_path = tmp_path / "good.json"
    data = {"foo": "bar"}
    config_path.write_text(json.dumps(data))
    cm = CONFIG_MANAGER(str(config_path))
    config = cm.load_config()
    assert config == data

def test_save_config_and_load(tmp_path):
    config_path = tmp_path / "save.json"
    cm = CONFIG_MANAGER(str(config_path))
    data = {"a": 1, "b": 2}
    cm.save_config(data)
    loaded = cm.load_config()
    assert loaded == data

def test_save_config_error(monkeypatch, tmp_path):
    config_path = tmp_path / "readonly.json"
    cm = CONFIG_MANAGER(str(config_path))
    data = {"fail": True}
    # Simulate open() failure
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(IOError("fail")))
    cm.save_config(data)

def test_unquote_basic():
    cm = CONFIG_MANAGER()
    assert cm.unquote("foo%20bar") == "foo bar"
    assert cm.unquote("test%40email.com") == "test@email.com"
    assert cm.unquote("%21%24%26") == "!$&"
    assert cm.unquote(123) == 123
