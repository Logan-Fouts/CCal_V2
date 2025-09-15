"""Unit tests for the AnimationRunner class in CCal_V2."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch
from animation_runner import AnimationRunner


class DummyLED:
    """Dummy LED class for testing AnimationRunner."""

    def __init__(self, num_leds=10, brightness=1.0):
        """Initialize DummyLED with number of LEDs and brightness."""
        self.num_leds = num_leds
        self.brightness = brightness
        self.calls = []

    def set_led(self, idx, color, brightness=None):
        """Mock set_led method."""
        self.calls.append(("set_led", idx, color, brightness))

    def fill(self, color, brightness=None):
        """Mock fill method."""
        self.calls.append(("fill", color, brightness))

    def turn_all_off(self):
        """Mock turn_all_off method."""
        self.calls.append(("turn_all_off",))


@pytest.fixture
def dummy_led():
    """Fixture for a DummyLED instance."""
    return DummyLED(num_leds=8, brightness=0.5)


@pytest.fixture
def runner(dummy_led):
    """Fixture for an AnimationRunner instance using DummyLED."""
    return AnimationRunner(dummy_led)


def test_turn_all_off(runner, dummy_led):
    """Test turn_all_off calls the correct LED method."""
    runner.turn_all_off()
    assert dummy_led.calls[-1][0] == "turn_all_off"


def test_color_wipe(runner, dummy_led):
    """Test color_wipe sets each LED and then turns all off."""
    with patch("time.sleep"):
        runner.color_wipe((1, 2, 3), 0.01)
    assert any(call[0] == "set_led" for call in dummy_led.calls)
    assert dummy_led.calls[-1][0] == "turn_all_off"


def test_theater_chase(runner, dummy_led):
    """Test theater_chase sets LEDs in chase pattern."""
    with patch("time.sleep"):
        runner.theater_chase((1, 2, 3), 0.01)
    assert any(call[0] == "set_led" for call in dummy_led.calls)


def test_wheel(runner):
    """Test wheel returns correct color tuples."""
    assert runner.wheel(0) == (0, 255, 0)
    assert runner.wheel(85) == (255, 0, 0)
    assert runner.wheel(170) == (0, 0, 255)


def test_rainbow_cycle(runner, dummy_led):
    """Test rainbow_cycle sets LEDs and turns all off."""
    with patch("time.sleep"):
        runner.rainbow_cycle(0, brightness=0.5)
    assert any(call[0] == "set_led" for call in dummy_led.calls)
    assert dummy_led.calls[-1][0] == "turn_all_off"


def test_flash(runner, dummy_led):
    """Test flash calls fill and turn_all_off."""
    with patch("time.sleep"):
        runner.flash()
    assert any(call[0] == "fill" for call in dummy_led.calls)
    assert any(call[0] == "turn_all_off" for call in dummy_led.calls)


def test_sun_animation_loop(runner, dummy_led):
    """Test sun_animation_loop sets LEDs."""
    with patch("time.sleep"), patch("time.time", side_effect=[0, 0.5, 1, 2]):
        runner.sun_animation_loop(end_time=1)
    assert any(call[0] == "set_led" for call in dummy_led.calls)


def test_cloud_animation_loop(runner, dummy_led):
    """Test cloud_animation_loop sets LEDs."""
    with patch("time.sleep"), patch("time.time", side_effect=[0, 0.5, 1, 2]):
        runner.cloud_animation_loop(end_time=1, brightness=0.5)
    assert any(call[0] == "set_led" for call in dummy_led.calls)


def test_rain_animation_loop(runner, dummy_led):
    """Test rain_animation_loop sets LEDs for rain drops."""
    with patch("time.sleep"), patch("time.time", side_effect=[0, 0.5, 1, 2]), patch(
        "random.random", return_value=0.5
    ), patch("random.randint", return_value=0):
        runner.rain_animation_loop(
            end_time=1, speed=1.0, drop_chance=1.0, brightness=0.5
        )
    assert any(call[0] == "set_led" for call in dummy_led.calls)


def test_snow_animation_loop(runner, dummy_led):
    """Test snow_animation_loop sets LEDs for snow drops."""
    with patch("time.sleep"), patch("time.time", side_effect=[0, 0.5, 1, 2]), patch(
        "random.random", return_value=0.5
    ), patch("random.randint", return_value=0):
        runner.snow_animation_loop(
            end_time=1, speed=1.0, drop_chance=1.0, brightness=0.5
        )
    assert any(call[0] == "set_led" for call in dummy_led.calls)


def test_thunderstorm_animation_loop(runner, dummy_led):
    """Test thunderstorm_animation_loop sets LEDs for thunderstorm effect."""
    with patch("time.sleep"), patch(
        "time.time", side_effect=[0, 0.5, 1, 5, 10, 15]
    ), patch("random.random", return_value=0.5), patch(
        "random.randint", return_value=0
    ):
        runner.thunderstorm_animation_loop(end_time=1, brightness=0.5)
    assert any(call[0] == "set_led" for call in dummy_led.calls)
