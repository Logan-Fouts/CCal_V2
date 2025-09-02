import board
import neopixel
import time
from animation_runner import AnimationRunner

class LED_UTILS:
    def __init__(self, num_days=7, animation=3, none_color=(255, 0, 0), event_color=(0, 255, 0), pin_num=18, brightness=1.0):
        self.num_leds = num_days
        self.animation = animation
        self.none_color = none_color
        self.event_color = event_color
        self.pin_num = pin_num
        self.brightness = max(0.0, min(1.0, float(brightness)))

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
        self.anim = AnimationRunner(self)
        self.turn_all_off()
        self.startup_animation()
        self.turn_all_off()

    def _apply_brightness(self, color, brightness=None):
        if brightness is None:
            brightness = self.brightness
        brightness = max(0.0, min(1.0, float(brightness)))
        return tuple(int(c * brightness) for c in color)

    def set_led(self, idx, color, brightness=None):
        color = self._apply_brightness(color, brightness)
        self.strip[idx] = color
        self.strip.show()

    def fill(self, color, brightness=None):
        color = self._apply_brightness(color, brightness)
        self.strip.fill(color)
        self.strip.show()

    def turn_all_off(self):
        """Turn off all LEDs."""
        self.strip.fill((0, 0, 0))
        self.strip.show()
        
    def display_number(self, number, color=(255, 255, 255), brightness=None):
        """Display a number using predefined digit patterns."""
        if brightness is None:
            brightness = self.brightness
        digit_patterns = {
            0: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27],
            1: [6, 5, 12, 19, 26, 27, 25],
            2: [4, 5, 6, 11, 19, 25, 26, 27],
            3: [4, 5, 6, 12, 18, 24, 26, 27],
            4: [6, 4, 11, 13, 18, 25, 12],
            5: [6, 13, 5, 4, 18, 25, 26, 27],
            6: [6, 13, 20, 27, 12, 26, 11, 18, 25],
            7: [6, 5, 4, 11, 19, 27],
            8: [4, 5, 6, 11, 13, 18, 20, 25, 26, 27, 19],
            9: [6, 5, 4, 11, 18, 25, 19, 20, 13]
        }

        str_num = str(number).zfill(2)[-2:]  # Ensure two digits

        # Display first digit
        first_digit = int(str_num[0])
        for idx in digit_patterns.get(first_digit, []):
            if 0 <= idx < self.num_leds:
                self.set_led(idx, color, brightness)

        # Display second digit (offset by -4)
        second_digit = int(str_num[1])
        for idx in digit_patterns.get(second_digit, []):
            idx2 = idx - 4
            if 0 <= idx2 < self.num_leds:
                self.set_led(idx2, color, brightness)

    def update_leds(self, event_counts):
        """Update LEDs based on event counts with optimized performance."""
        if not event_counts:
            return
        
        max_count = max(event_counts)
        if max_count == 0:
            for day in range(min(self.num_leds, len(event_counts))):
                self.set_led(day, self.none_color, self.brightness * 0.05)
            return
        
        # Adjust brightness based on time of day
        # TODO: Maybe use a light sensor instead of time?
        current_hour = time.localtime().tm_hour
        is_night = current_hour >= 22 or current_hour <= 8
        max_brightness = self.brightness * (0.1 if is_night else self.brightness)
        
        updates = []
        for day in range(min(self.num_leds, len(event_counts))):
            count = event_counts[day]
            if count > 0:
                brightness = 0.1 + max_brightness * (count / max_count)
                updates.append((day, self.event_color, brightness))
            else:
                updates.append((day, self.none_color, max((max_brightness * 0.05), 0.05)))

        # Apply all updates
        for day, color, brightness in updates:
            self.set_led(day, color, brightness)

    def update_leds_for_events(self, event_counts):
        max_events = max(event_counts) if event_counts else 1
        for i, count in enumerate(event_counts):
            # Scale brightness: 0 events = 0.2, max events = self.brightness
            if max_events > 0:
                scaled_brightness = 0.2 + 0.8 * (count / max_events) * self.brightness
            else:
                scaled_brightness = 0.2 * self.brightness
            self.set_led(i, self.event_color, scaled_brightness)

    def _dim(self, color, factor=0.2):
        """Return a color tuple dimmed by the given factor (0.0 - 1.0)."""
        return tuple(int(c * factor) for c in color)

    def startup_animation(self):
        """Run a startup animation based on self.animation setting using AnimationRunner."""
        dim = lambda color: self._dim(color, 0.2)
        if self.animation == 1:
            self.anim.color_wipe(dim((255, 0, 0)), 0.05)
            self.anim.color_wipe(dim((0, 255, 0)), 0.05)
            self.anim.color_wipe(dim((0, 0, 255)), 0.05)
        elif self.animation == 2:
            self.anim.theater_chase(dim((127, 127, 127)), 0.05)
        elif self.animation == 3:
            print("Running rainbow")
            self.anim.rainbow_cycle(0.01, brightness=0.2)
        else:
            for color in [(255,0,0), (0,255,0), (0,0,255)]:
                self.anim.fill(dim(color), int(self.brightness * 0.3))
                time.sleep(0.5)
        self.turn_all_off()

    def show_weather(self, weather_status, brightness=None, duration_sec=5):
        """Display weather animation for specified duration with adjustable brightness.
        
        Args:
            weather_status (dict): Dict with 'condition' and 'temperature'
            duration_sec (float): How long to run animation (default: 5 seconds)
            brightness (int): Overall brightness scaling (0-100, defaults to instance brightness)
        """
        if brightness is None:
            brightness = self.brightness

        if not weather_status or not isinstance(weather_status, dict):
            return

        condition = weather_status.get('condition', '').lower()
        temperature = weather_status.get('temperature', None)
        end_time = time.time() + duration_sec

        # Use AnimationRunner for all animations
        if condition == 'clear':
            self.anim.sun_animation_loop(end_time, brightness)
        elif condition == 'clouds':
            self.anim.cloud_animation_loop(end_time, brightness)
        elif condition == 'rain':
            self.anim.rain_animation_loop(end_time, speed=1.0, drop_chance=0.9, brightness=brightness)
        elif condition == 'drizzle':
            self.anim.rain_animation_loop(end_time, speed=0.5, drop_chance=0.2, brightness=brightness)
        elif condition == 'snow':
            self.anim.snow_animation_loop(end_time, brightness=brightness)
        elif condition == 'thunderstorm':
            self.anim.thunderstorm_animation_loop(end_time, brightness)
        elif condition in ('mist', 'fog'):
            self.anim.fog_animation_loop(end_time, brightness)
        else:
            self.anim.default_animation_loop(end_time, brightness)

        self.turn_all_off()

        if temperature is not None:
            try:
                temp_int = int(round(temperature))
                if temp_int < 0:
                    color = (0, 200, 255)
                elif temp_int < 19:
                    color = (255, 255, 255) 
                else:
                    color = (0, 255, 0)
                self.display_number(temp_int, color=color, brightness=brightness)
                time.sleep(5)
                self.turn_all_off()
            except Exception as e:
                print(f"Error displaying temperature: {e}")

