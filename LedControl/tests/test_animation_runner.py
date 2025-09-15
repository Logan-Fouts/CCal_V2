import pytest
from unittest.mock import MagicMock, patch
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from animation_runner import AnimationRunner

class DummyLED:
    def __init__(self, num_leds=10, brightness=1.0):
        self.num_leds = num_leds
        self.brightness = brightness
        self.calls = []
    def set_led(self, idx, color, brightness=None):
        self.calls.append(('set_led', idx, color, brightness))
    def fill(self, color, brightness=None):
        self.calls.append(('fill', color, brightness))
    def turn_all_off(self):
        self.calls.append(('turn_all_off',))

@pytest.fixture
def dummy_led():
    return DummyLED(num_leds=8, brightness=0.5)

@pytest.fixture
def runner(dummy_led):
    return AnimationRunner(dummy_led)

def test_turn_all_off(runner, dummy_led):
    runner.turn_all_off()
    assert dummy_led.calls[-1][0] == 'turn_all_off'

def test_color_wipe(runner, dummy_led):
    with patch('time.sleep'):
        runner.color_wipe((1,2,3), 0.01)
    # Should call set_led for each LED and then turn_all_off
    assert any(call[0] == 'set_led' for call in dummy_led.calls)
    assert dummy_led.calls[-1][0] == 'turn_all_off'

def test_theater_chase(runner, dummy_led):
    with patch('time.sleep'):
        runner.theater_chase((1,2,3), 0.01)
    # Should call set_led for each LED
    assert any(call[0] == 'set_led' for call in dummy_led.calls)

def test_wheel(runner):
    assert runner.wheel(0) == (0,255,0)
    assert runner.wheel(85) == (255,0,0)
    assert runner.wheel(170) == (0,0,255)

def test_rainbow_cycle(runner, dummy_led):
    with patch('time.sleep'):
        runner.rainbow_cycle(0, brightness=0.5)
    # Should call set_led for each LED
    assert any(call[0] == 'set_led' for call in dummy_led.calls)
    assert dummy_led.calls[-1][0] == 'turn_all_off'

def test_flash(runner, dummy_led):
    with patch('time.sleep'):
        runner.flash()
    # Should call fill and turn_all_off
    assert any(call[0] == 'fill' for call in dummy_led.calls)
    assert any(call[0] == 'turn_all_off' for call in dummy_led.calls)

def test_sun_animation_loop(runner, dummy_led):
    with patch('time.sleep'), patch('time.time', side_effect=[0,0.5,1,2]):
        runner.sun_animation_loop(end_time=1)
    assert any(call[0] == 'set_led' for call in dummy_led.calls)

def test_cloud_animation_loop(runner, dummy_led):
    with patch('time.sleep'), patch('time.time', side_effect=[0,0.5,1,2]):
        runner.cloud_animation_loop(end_time=1, brightness=0.5)
    assert any(call[0] == 'set_led' for call in dummy_led.calls)

def test_rain_animation_loop(runner, dummy_led):
    with patch('time.sleep'), patch('time.time', side_effect=[0,0.5,1,2]), patch('random.random', return_value=0.5), patch('random.randint', return_value=0):
        runner.rain_animation_loop(end_time=1, speed=1.0, drop_chance=1.0, brightness=0.5)
    assert any(call[0] == 'set_led' for call in dummy_led.calls)

def test_snow_animation_loop(runner, dummy_led):
    with patch('time.sleep'), patch('time.time', side_effect=[0,0.5,1,2]), patch('random.random', return_value=0.5), patch('random.randint', return_value=0):
        runner.snow_animation_loop(end_time=1, speed=1.0, drop_chance=1.0, brightness=0.5)
    assert any(call[0] == 'set_led' for call in dummy_led.calls)

def test_thunderstorm_animation_loop(runner, dummy_led):
    with patch('time.sleep'), patch('time.time', side_effect=[0,0.5,1,5,10,15]), patch('random.random', return_value=0.5), patch('random.randint', return_value=0):
        runner.thunderstorm_animation_loop(end_time=1, brightness=0.5)
    assert any(call[0] == 'set_led' for call in dummy_led.calls)
