import sys
import os
from unittest.mock import patch, MagicMock
import pytest

# Patch Pi-specific modules for import
sys.modules['board'] = MagicMock()
sys.modules['neopixel'] = MagicMock()

# Patch other modules used in main
sys.modules['animation_runner'] = MagicMock()
sys.modules['weather_tracker'] = MagicMock()


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

@patch('main.CONFIG_MANAGER')
@patch('main.LED_UTILS')
@patch('main.GITHUB_TRACKER')
@patch('main.WEATHER_TRACKER')
def test_main_runs_with_minimal_config(mock_weather, mock_gh, mock_led, mock_config_mgr):
    # Setup config
    config = {
        'POLL_TIME': 1,
        'PIN_NUM': 18,
        'NUM_DAYS': 2,
        'NONE_COLOR': [1,2,3],
        'EVENT_COLOR': [4,5,6],
        'BRIGHTNESS': 0.8,
        'ON_TIME': 0,
        'OFF_TIME': 24,
        'OPENWEATHERMAP_API_KEY': 'k',
        'WEATHER_LAT': 1,
        'WEATHER_LON': 2,
        'STARTUP_ANIMATION': 1
    }
    mock_config_mgr.return_value.load_config.return_value = config
    mock_led.return_value = MagicMock()
    mock_gh.return_value.fetch_github_events.return_value = [1,2]
    mock_weather.return_value.get_weather.return_value = {'condition': 'clear', 'temperature': 10}
    # Patch time.sleep to break loop after first iteration
    with patch('main.time.sleep', side_effect=KeyboardInterrupt):
        main.main()
    # All components should be initialized
    mock_led.assert_called()
    mock_gh.assert_called()
    mock_weather.assert_called()

@patch('main.CONFIG_MANAGER')
def test_main_missing_required_config(mock_config_mgr):
    # Missing required weather config
    config = {'POLL_TIME': 1, 'PIN_NUM': 18, 'NUM_DAYS': 2, 'NONE_COLOR': [1,2,3], 'EVENT_COLOR': [4,5,6], 'BRIGHTNESS': 0.8, 'ON_TIME': 0, 'OFF_TIME': 24}
    mock_config_mgr.return_value.load_config.return_value = config
    with patch('main.sys.exit', side_effect=SystemExit) as exit_mock:
        with pytest.raises(SystemExit):
            main.main()
        exit_mock.assert_called()

@patch('main.CONFIG_MANAGER')
def test_main_config_load_error(mock_config_mgr):
    mock_config_mgr.side_effect = Exception('fail')
    with patch('main.sys.exit', side_effect=SystemExit) as exit_mock:
        with pytest.raises(SystemExit):
            main.main()
        exit_mock.assert_called()
