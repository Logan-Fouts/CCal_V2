import sys
import types
# Mock board and neopixel modules before importing AnimationRunner
sys.modules["board"] = types.ModuleType("board")
sys.modules["neopixel"] = types.ModuleType("neopixel")

import pytest
from unittest.mock import MagicMock, patch


from led_control.core.animation_runner import AnimationRunner

@pytest.fixture
def mock_led():
	led = MagicMock()
	led.num_leds = 5
	return led

def test_turn_all_off_calls_led(mock_led):
	runner = AnimationRunner(mock_led)
	runner.turn_all_off()
	mock_led.turn_all_off.assert_called_once()

@patch("time.sleep", return_value=None)
def test_color_wipe(mock_sleep, mock_led):
	runner = AnimationRunner(mock_led)
	runner.num_leds = 3
	runner.led.num_leds = 3
	runner.color_wipe((1, 2, 3), wait=0.01, brightness=0.5)
	# Should set each pixel, show, then turn all off
	assert mock_led.set_pixel.call_count == 3
	assert mock_led.show.call_count == 3
	mock_led.turn_all_off.assert_called_once()

@patch("time.sleep", return_value=None)
def test_theater_chase(mock_sleep, mock_led):
	runner = AnimationRunner(mock_led)
	runner.num_leds = 6
	runner.led.num_leds = 6
	runner.theater_chase((10, 20, 30), wait=0.01, brightness=0.7)
	# Should call set_pixel and show multiple times
	assert mock_led.set_pixel.call_count > 0
	assert mock_led.show.call_count > 0

@patch("time.sleep", return_value=None)
def test_rainbow_cycle(mock_sleep, mock_led):
	runner = AnimationRunner(mock_led)
	runner.num_leds = 2
	runner.led.num_leds = 2
	runner.rainbow_cycle(wait=0.0, brightness=1.0)
	# Should set each pixel and show for each j in range(256)
	assert mock_led.set_pixel.call_count == 2 * 256
	assert mock_led.show.call_count == 256
	mock_led.turn_all_off.assert_called_once()

@patch("time.sleep", return_value=None)
def test_cloud_animation_loop(mock_sleep, mock_led):
	runner = AnimationRunner(mock_led)
	runner.num_leds = 30
	runner.led.num_leds = 30
	# Run for a very short time
	with patch("time.time", side_effect=[0, 0, 1, 2, 3, 4, 5, 6]):
		runner.cloud_animation_loop(end_time=2, brightness=0.5)
	assert mock_led.set_pixel.call_count > 0
	assert mock_led.show.call_count > 0
	assert mock_led.turn_all_off.call_count > 0
