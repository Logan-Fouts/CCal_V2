from unittest.mock import MagicMock

import pytest
import time


# Reset the NeoPixel mock before each test to avoid test pollution
@pytest.fixture(autouse=True)
def reset_neopixel_mock():
    import sys

    sys.modules["neopixel"].NeoPixel.reset_mock()


from led_control.core.led_controller import LEDController


def test_init_sets_attributes_and_creates_strip():
    time.sleep(1) # Fixes occasional test failure due to neopixel mock issues
    controller = LEDController(pin_num=18, num_leds=10, brightness=0.7)
    assert controller.num_leds == 10
    assert controller.brightness == 0.7
    # NeoPixel should be called with correct args
    import sys

    args, kwargs = sys.modules["neopixel"].NeoPixel.call_args
    # The first argument should be the gpio_pin, which is mock_board.D18 ("D18_PIN")
    assert args[0] == "D18_PIN"
    assert args[1] == 10
    assert kwargs["brightness"] == 1.0
    assert kwargs["auto_write"] is False
    assert kwargs["pixel_order"] == "GRB"
    assert hasattr(controller, "strip")


def test_apply_brightness_scales_color():
    controller = LEDController()
    color = (100, 200, 50)
    # Default brightness is 1.0
    assert controller._apply_brightness(color) == (100, 200, 50)
    # Custom brightness
    assert controller._apply_brightness(color, 0.5) == (50, 100, 25)
    # Clamp brightness
    assert controller._apply_brightness(color, 2.0) == (100, 200, 50)
    assert controller._apply_brightness(color, -1.0) == (0, 0, 0)


def test_set_pixel_sets_strip_pixel():
    controller = LEDController(num_leds=5)
    controller.strip = MagicMock()
    controller.set_pixel(2, (10, 20, 30), brightness=0.5)
    # Should apply brightness and set pixel
    controller.strip.__setitem__.assert_called_with(2, (5, 10, 15))


def test_set_pixel_out_of_range_does_nothing():
    controller = LEDController(num_leds=3)
    controller.strip = MagicMock()
    controller.set_pixel(5, (1, 2, 3))
    controller.strip.__setitem__.assert_not_called()


def test_set_pixels_sets_multiple():
    controller = LEDController(num_leds=3)
    controller.set_pixel = MagicMock()
    pixels = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    controller.set_pixels(pixels, brightness=0.8)
    controller.set_pixel.assert_any_call(0, (1, 2, 3), 0.8)
    controller.set_pixel.assert_any_call(1, (4, 5, 6), 0.8)
    controller.set_pixel.assert_any_call(2, (7, 8, 9), 0.8)


def test_fill_calls_strip_fill():
    controller = LEDController(num_leds=2)
    controller.strip = MagicMock()
    controller.fill((10, 20, 30), brightness=0.5)
    controller.strip.fill.assert_called_with((5, 10, 15))


def test_show_calls_strip_show():
    controller = LEDController()
    controller.strip = MagicMock()
    controller.show()
    controller.strip.show.assert_called_once()


def test_turn_all_off_fills_and_shows():
    controller = LEDController()
    controller.strip = MagicMock()
    controller.turn_all_off()
    controller.strip.fill.assert_called_with((0, 0, 0))
    controller.strip.show.assert_called_once()


def test_cleanup_turns_all_off():
    controller = LEDController()
    controller.turn_all_off = MagicMock()
    controller.cleanup()
    controller.turn_all_off.assert_called_once()
