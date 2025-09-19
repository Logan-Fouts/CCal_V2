import pytest
import led_control.utils.led_utils as led_utils


def test_hex_to_rgb():
    assert led_utils.hex_to_rgb("#ffffff") == (255, 255, 255)
    assert led_utils.hex_to_rgb("000000") == (0, 0, 0)
    assert led_utils.hex_to_rgb("#123456") == (18, 52, 86)


@pytest.mark.parametrize(
    "color,brightness,expected",
    [
        ((100, 200, 50), 1.0, (100, 200, 50)),
        ((100, 200, 50), 0.5, (50, 100, 25)),
        ((100, 200, 50), 0.0, (0, 0, 0)),
        ((100, 200, 50), 2.0, (100, 200, 50)),
        ((100, 200, 50), -1.0, (0, 0, 0)),
    ],
)
def test_apply_brightness(color, brightness, expected):
    assert led_utils.apply_brightness(color, brightness) == expected


def test_fade_color():
    assert led_utils.fade_color((0, 0, 0), (255, 255, 255), 0.0) == (0, 0, 0)
    assert led_utils.fade_color((0, 0, 0), (255, 255, 255), 1.0) == (255, 255, 255)
    assert led_utils.fade_color((0, 0, 0), (255, 0, 0), 0.5) == (127, 0, 0)
    assert led_utils.fade_color((10, 20, 30), (20, 40, 60), 0.5) == (15, 30, 45)


def test_create_gradient():
    grad = led_utils.create_gradient((0, 0, 0), (255, 255, 255), 3)
    assert grad[0] == (0, 0, 0)
    assert grad[-1] == (255, 255, 255)
    assert grad[1] == (127, 127, 127)
    # num_leds=1 should return just the start color
    grad = led_utils.create_gradient((10, 20, 30), (40, 50, 60), 1)
    assert grad == [(10, 20, 30)]


def test_get_digit_patterns():
    patterns = led_utils.get_digit_patterns()
    assert isinstance(patterns, dict)
    for k, v in patterns.items():
        assert isinstance(k, int)
        assert isinstance(v, list)
        for idx in v:
            assert isinstance(idx, int)


@pytest.mark.parametrize(
    "hour,base,expected",
    [
        (23, 1.0, 0.1),
        (8, 1.0, 0.1),
        (9, 1.0, 1.0),
        (21, 0.5, 0.5),
        (22, 0.5, 0.05),
        (7, 0.5, 0.05),
    ],
)
def test_calculate_time_based_brightness(hour, base, expected):
    assert (
        pytest.approx(led_utils.calculate_time_based_brightness(hour, base), 0.01)
        == expected
    )


@pytest.mark.parametrize(
    "temp,expected",
    [
        (-5, (0, 200, 255)),
        (0, (255, 255, 255)),
        (10, (255, 255, 255)),
        (19, (0, 255, 0)),
        (30, (0, 255, 0)),
    ],
)
def test_get_temperature_color(temp, expected):
    assert led_utils.get_temperature_color(temp) == expected
