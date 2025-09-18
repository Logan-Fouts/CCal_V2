"""Unit tests for the LedUtils class in CCal_V2."""

import sys
import os
from unittest.mock import patch, MagicMock
import pytest

sys.modules["board"] = MagicMock()
sys.modules["neopixel"] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from led_utils import LedUtils


@pytest.fixture
def mock_strip_fixture():
    """Fixture for mocking a NeoPixel strip.""" 
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_anim_fixture():
    """Fixture for mocking an AnimationRunner."""
    mock = MagicMock()
    return mock


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_led_utils_init(mock_anim_runner, mock_neopixel):
    """Test LedUtils initialization and attribute assignment."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    mock_anim = MagicMock()
    mock_anim_runner.return_value = mock_anim
    led = LedUtils(
        num_days=5,
        animation=1,
        none_color=(1, 2, 3),
        event_color=(4, 5, 6),
        pin_num=18,
        brightness=0.5,
    )
    assert led.num_leds == 5
    assert led.none_color == (1, 2, 3)
    assert led.event_color == (4, 5, 6)
    assert led.brightness == 0.5
    mock_neopixel.assert_called_once()
    mock_anim_runner.assert_called_once_with(led)
    mock_strip.fill.assert_called()
    mock_strip.show.assert_called()


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_set_led_and_fill(mock_anim_runner, mock_neopixel):
    """Test set_led and fill methods for correct color and brightness application."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    led = LedUtils(num_days=3)
    led.set_led(1, (10, 20, 30), brightness=0.5)
    mock_strip.__setitem__.assert_called_with(1, (5, 10, 15))
    mock_strip.show.assert_called()
    led.fill((100, 200, 50), brightness=0.2)
    mock_strip.fill.assert_called_with((20, 40, 10))


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_turn_all_off(mock_anim_runner, mock_neopixel):
    """Test turn_all_off turns all LEDs off."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    led = LedUtils(num_days=2)
    led.turn_all_off()
    mock_strip.fill.assert_called_with((0, 0, 0))
    mock_strip.show.assert_called()


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_update_leds_none(mock_anim_runner, mock_neopixel):
    """Test update_leds with all zero event counts."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    led = LedUtils(num_days=2)
    led.set_led = MagicMock()
    led.update_leds([0, 0])
    assert led.set_led.call_count == 2


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_update_leds_some(mock_anim_runner, mock_neopixel):
    """Test update_leds with nonzero event counts."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    led = LedUtils(num_days=2)
    led.set_led = MagicMock()
    led.update_leds([1, 2])
    assert led.set_led.call_count == 2


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_update_leds_for_events(mock_anim_runner, mock_neopixel):
    """Test update_leds_for_events scales brightness by event count."""
    mock_strip = MagicMock()
    mock_neopixel.return_value = mock_strip
    led = LedUtils(num_days=3)
    led.set_led = MagicMock()
    led.update_leds_for_events([0, 1, 2])
    assert led.set_led.call_count == 3


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_dim(mock_anim_runner, mock_neopixel):
    """Test _dim returns a dimmed color tuple."""
    led = LedUtils(num_days=1)
    assert led._dim((100, 200, 50), 0.5) == (50, 100, 25)


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_apply_brightness(mock_anim_runner, mock_neopixel):
    """Test _apply_brightness returns a color tuple with applied brightness."""
    led = LedUtils(num_days=1)
    assert led._apply_brightness((100, 200, 50), 0.5) == (50, 100, 25)


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_display_number(mock_anim_runner, mock_neopixel):
    """Test display_number calls set_led for digits."""
    led = LedUtils(num_days=30)
    led.set_led = MagicMock()
    led.display_number(12, color=(1, 2, 3), brightness=0.5)
    assert led.set_led.call_count > 0


@patch("led_utils.neopixel.NeoPixel")
@patch("led_utils.board.D18", new=1)
@patch("led_utils.AnimationRunner")
def test_show_weather_calls_anim(mock_anim_runner, mock_neopixel):
    """Test show_weather calls the correct animation methods and display_number."""
    led = LedUtils(num_days=5)
    anim = MagicMock()
    led.anim = anim
    led.turn_all_off = MagicMock()
    # Each condition should call the right anim method
    led.show_weather(
        {"condition": "clear", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.sun_animation_loop.assert_called()
    led.show_weather(
        {"condition": "clouds", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.cloud_animation_loop.assert_called()
    led.show_weather(
        {"condition": "rain", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.rain_animation_loop.assert_called()
    led.show_weather(
        {"condition": "drizzle", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.rain_animation_loop.assert_called()
    led.show_weather(
        {"condition": "snow", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.snow_animation_loop.assert_called()
    led.show_weather(
        {"condition": "thunderstorm", "temperature": 10},
        brightness=0.5,
        duration_sec=0.01,
    )
    anim.thunderstorm_animation_loop.assert_called()
    led.show_weather(
        {"condition": "mist", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.fog_animation_loop.assert_called()
    led.show_weather(
        {"condition": "unknown", "temperature": 10}, brightness=0.5, duration_sec=0.01
    )
    anim.default_animation_loop.assert_called()
    # Should call display_number for temperature
    led.display_number = MagicMock()
    led.show_weather(
        {"condition": "clear", "temperature": 5}, brightness=0.5, duration_sec=0.01
    )
    led.display_number.assert_called()
    # Should not fail if weather_status is None or not dict
    led.show_weather(None)
    led.show_weather(123)
