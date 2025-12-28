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

    def display_number(self, number, color=(255, 255, 255)):
        """Display a number using predefined digit patterns."""
        digit_patterns = {
            0: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27],
            1: [6, 5, 12, 19, 26, 27, 25],
            2: [4, 5, 6, 11, 19, 25, 26, 27],
            3: [4, 5, 6, 12, 18, 26, 27],
            4: [6, 4, 11, 13, 18, 25, 12],
            5: [6, 13, 5, 4, 18, 25, 26, 27],
            6: [6, 13, 20, 27, 12, 26, 11, 18, 25],
            7: [6, 5, 4, 11, 19, 27],
            8: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27, 19],
            9: [6, 5, 4, 11, 18, 25, 19, 20, 13],
        }
    
        # Handle negative temperature
        if number < 0:
            number = abs(number)  # Use absolute value
            color = (128, 0, 128)  # Dark purple color for negative temps
    
        str_num = str(number).zfill(2)[-2:]  # Ensure two digits
    
        # Display first digit
        first_digit = int(str_num[0])
        for idx in digit_patterns.get(first_digit, []):
            if 0 <= idx < self.num_leds:
                self.set_pixel(idx, color)
    
        # Display second digit (offset by -4)
        second_digit = int(str_num[1])
        for idx in digit_patterns.get(second_digit, []):
            idx2 = idx - 4
            if 0 <= idx2 < self.num_leds:
                self.set_pixel(idx2, color)

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
