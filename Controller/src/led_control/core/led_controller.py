import math
import time
from typing import Tuple, Optional
from led_control.core.led_controller import LEDController


class AnimationRunner:
    """Runs various LED animations using LED controller."""

    def __init__(self, led_controller: LEDController):
        self.led = led_controller
        self.num_leds = led_controller.num_leds

    def turn_all_off(self):
        """Turn off all LEDs."""
        self.led.turn_all_off()

    def sun_animation_loop(self, end_time: float, brightness: Optional[float] = None):
        """Run sun animation until end_time."""
        colors = [(255, 255, 0), (255, 255, 50), (255, 255, 20)]
        ray_pattern = [0, 1, 2] * ((self.num_leds // 3) + 1)

        while time.time() < end_time:
            cycle_time = time.time()
            cycle_progress = (cycle_time % 2) / 2
            core_brightness = 0.3 + 0.7 * (
                0.5 + 0.5 * math.sin(cycle_progress * math.pi)
            )
            wave_pos = int(cycle_progress * 3) % 3

            for i in range(self.num_leds):
                dist_from_center = abs(i - self.num_leds // 2)
                color_idx = ray_pattern[i]
                wave_effect = (3 - (dist_from_center + wave_pos) % 3) * 0.3
                led_brightness = min(1.0, core_brightness + wave_effect)
                self.led.set_pixel(
                    i,
                    colors[color_idx],
                    brightness * led_brightness if brightness else led_brightness,
                )

            self.led.show()
            time.sleep(0.05)

    def cloud_animation_loop(self, end_time: float, brightness: Optional[float] = None):
        """Run cloud animation until end_time."""
        cloud_colors = [(180, 180, 180), (220, 220, 220), (255, 255, 255)]
        cloud = [12, 11, 20, 19, 18, 17]

        self.turn_all_off()
        while time.time() < end_time:
            for i in range(0, 4):
                for pixel in cloud:
                    if 0 <= pixel - i < self.num_leds:
                        self.led.set_pixel(pixel - i, cloud_colors[0], brightness)
                self.led.show()
                time.sleep(0.5)
                self.turn_all_off()

    # [Include other animation methods with similar pattern - rain, snow, etc.]
    # Methods should use self.led.set_pixel() and self.led.show()

    def color_wipe(
        self,
        color: Tuple[int, int, int],
        wait: float,
        brightness: Optional[float] = None,
    ):
        """Wipe color across display one LED at a time."""
        for i in range(self.num_leds):
            self.led.set_pixel(i, color, brightness)
            self.led.show()
            time.sleep(wait)
        self.turn_all_off()

    def theater_chase(
        self,
        color: Tuple[int, int, int],
        wait: float,
        brightness: Optional[float] = None,
    ):
        """Theater chase animation."""
        spacing = 3
        cycles = 15

        for phase in range(spacing):
            for _ in range(cycles):
                for i in range(self.num_leds):
                    if (i + phase) % spacing == 0:
                        self.led.set_pixel(i, color, brightness)
                    else:
                        self.led.set_pixel(i, (0, 0, 0), brightness)
                self.led.show()
                time.sleep(wait)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    def rainbow_cycle(self, wait: float, brightness: float = 1.0):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256):
            for i in range(self.num_leds):
                pixel_index = (i * 256 // self.num_leds) + j
                color = self.wheel(pixel_index & 255)
                self.led.set_pixel(i, color, brightness)
            self.led.show()
            time.sleep(wait)
        self.turn_all_off()
import board
import neopixel
from typing import List, Tuple, Optional


class LEDController:
    """Low-level hardware interface for NeoPixel LEDs."""

    def __init__(self, pin_num: int = 18, num_leds: int = 28, brightness: float = 1.0):
        self.num_leds = num_leds
        self.brightness = max(0.0, min(1.0, float(brightness)))

        if -1 < pin_num < 28:
            gpio_pin = getattr(board, f"D{pin_num}")  

        self.strip = neopixel.NeoPixel(
            gpio_pin,
            self.num_leds,
            brightness=1.0,
            auto_write=False,
            pixel_order=neopixel.GRB,
        )

    def _apply_brightness(
        self, color: Tuple[int, int, int], brightness: Optional[float] = None
    ) -> Tuple[int, int, int]:
        """Apply brightness scaling to a color tuple."""
        if brightness is None:
            brightness = self.brightness
        brightness = max(0.0, min(1.0, float(brightness)))
        return tuple(int(c * brightness) for c in color)

    def set_pixel(
        self, idx: int, color: Tuple[int, int, int], brightness: Optional[float] = None
    ):
        """Set a single LED to a color with optional brightness."""
        if 0 <= idx < self.num_leds:
            color = self._apply_brightness(color, brightness)
            self.strip[idx] = color

    def set_pixels(
        self, pixels: List[Tuple[int, int, int]], brightness: Optional[float] = None
    ):
        """Set multiple LEDs at once."""
        for i, color in enumerate(pixels):
            if i < self.num_leds:
                self.set_pixel(i, color, brightness)

    def fill(self, color: Tuple[int, int, int], brightness: Optional[float] = None):
        """Fill all LEDs with a color and optional brightness."""
        color = self._apply_brightness(color, brightness)
        self.strip.fill(color)

    def show(self):
        """Update the LED strip with current colors."""
        self.strip.show()

    def turn_all_off(self):
        """Turn off all LEDs."""
        self.strip.fill((0, 0, 0))
        self.strip.show()

    def cleanup(self):
        """Clean up resources."""
        self.turn_all_off()
