import board
import neopixel
import time
import random

class LED_UTILS:
    def __init__(self, num_days=7, animation=3, none_color=(255, 0, 0), event_color=(0, 255, 0), pin_num=18):
        self.num_leds = num_days
        self.animation = animation
        self.none_color = none_color
        self.event_color = event_color

        # Map pin_num to board pin
        if pin_num == 18:
            gpio_pin = board.D18
        else:
            raise ValueError("Only GPIO18 supported by default. Update mapping for other pins.")

        self.strip = neopixel.NeoPixel(
            gpio_pin,
            self.num_leds,
            brightness=1.0,
            auto_write=False,
            pixel_order=neopixel.GRB
        )
        self.turn_all_off()
        self.startup_animation()
        self.turn_all_off()

    def set_led(self, led_index, color, brightness=50):
        r, g, b = color
        brightness = max(0, min(100, brightness)) / 100.0
        self.strip[led_index] = (int(r * brightness), int(g * brightness), int(b * brightness))
        self.strip.show()

    def fill(self, color, brightness=50):
        r, g, b = color
        brightness = max(0, min(100, brightness)) / 100.0
        self.strip.fill((int(r * brightness), int(g * brightness), int(b * brightness)))
        self.strip.show()

    def turn_all_off(self):
        self.strip.fill((0, 0, 0))
        self.strip.show()

    def update_leds(self, event_counts):
        max_count = max(event_counts) if event_counts else 1
        current_time = time.localtime()
        for day in range(min(self.num_leds, len(event_counts))):
            count = event_counts[day]
            if count > 0:
                if current_time.tm_hour >= 22 or current_time.tm_hour <= 8:
                    brightness = 1 + int(10 * (count / max_count))
                else:
                    brightness = 1 + int(80 * (count / max_count))
                self.set_led(day, self.event_color, brightness)
            else:
                self.set_led(day, self.none_color, 5)
            time.sleep(0.05)

    def _dim(self, color, factor=0.2):
        """Return a color tuple dimmed by the given factor (0.0 - 1.0)."""
        return tuple(int(c * factor) for c in color)

    def startup_animation(self):
        """Run a startup animation based on self.animation setting."""
        dim = lambda color: self._dim(color, 0.2)
        if self.animation == 1:
            self.color_wipe(dim((255, 0, 0)), 0.05)
            self.color_wipe(dim((0, 255, 0)), 0.05)
            self.color_wipe(dim((0, 0, 255)), 0.05)
        elif self.animation == 2:
            self.theater_chase(dim((127, 127, 127)), 0.05)
        elif self.animation == 3:
            self.rainbow_cycle(0.01, brightness=0.2)
        else:
            # Default: simple cycle
            for color in [(255,0,0), (0,255,0), (0,0,255)]:
                self.fill(dim(color), 30)
                time.sleep(0.5)
        self.turn_all_off()

    def color_wipe(self, color, wait):
        """Wipe color across display a pixel at a time."""
        for i in range(self.num_leds):
            self.strip[i] = color
            self.strip.show()
            time.sleep(wait)
        self.turn_all_off()

    def theater_chase(self, color, wait):
        """Movie theater light style chaser animation."""
        for q in range(10):
            for i in range(0, self.num_leds, 3):
                self.strip[i] = color
            self.strip.show()
            time.sleep(wait)
            for i in range(0, self.num_leds, 3):
                self.strip[i] = (0, 0, 0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        elif pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        else:
            pos -= 170
            return (0, int(pos * 3), int(255 - pos * 3))

    def rainbow_cycle(self, wait, brightness=1.0):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256):
            for i in range(self.num_leds):
                pixel_index = (i * 256 // self.num_leds) + j
                color = self.wheel(pixel_index & 255)
                color = self._dim(color, brightness)
                self.strip[i] = color
            self.strip.show()
            time.sleep(wait)
        self.turn_all_off()
