import board
import neopixel
import time
import random
import math
import random
from collections import deque

class LED_UTILS:
    def __init__(self, num_days=7, animation=3, none_color=(255, 0, 0), event_color=(0, 255, 0), pin_num=18):
        self.num_leds = num_days
        self.animation = animation
        self.none_color = none_color
        self.event_color = event_color

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
        """Update LEDs based on event counts with optimized performance."""
        if not event_counts:
            return
        
        max_count = max(event_counts)
        if max_count == 0:
            for day in range(min(self.num_leds, len(event_counts))):
                self.set_led(day, self.none_color, 5)
            self.strip.show()
            return
        
        current_hour = time.localtime().tm_hour
        is_night = current_hour >= 22 or current_hour <= 8
        max_brightness = 10 if is_night else 80
        
        updates = []
        for day in range(min(self.num_leds, len(event_counts))):
            count = event_counts[day]
            if count > 0:
                brightness = 1 + int(max_brightness * (count / max_count))
                updates.append((day, self.event_color, brightness))
            else:
                updates.append((day, self.none_color, 5))
        
        # Apply all updates at once
        for day, color, brightness in updates:
            self.set_led(day, color, brightness)
        
        self.strip.show()

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

    def flash(self):
            """Cooler, dimmer flash animation: soft pulse, then a pastel color wave with fading tail."""
            for _ in range(2):
                self.fill((180, 180, 180), 8)
                time.sleep(0.10)
                self.turn_all_off()
                time.sleep(0.07)
            pastel_colors = [
                (120, 180, 255), (180, 255, 200), (255, 180, 220),
                (200, 120, 255), (255, 240, 180), (180, 255, 255)
            ]
            num_rows = 4
            num_cols = 7
            fade_steps = 4
            for color in pastel_colors:
                for row in range(num_rows):
                    if row % 2 == 0:
                        indices = list(range(num_cols * row, num_cols * (row + 1)))
                    else:
                        indices = list(range(num_cols * (row + 1) - 1, num_cols * row - 1, -1))
                    for idx, i in enumerate(indices):
                        if i < self.num_leds:
                            for tail in range(fade_steps):
                                tail_idx = idx - tail
                                if tail_idx >= 0:
                                    led = indices[tail_idx]
                                    fade = max(0.15, 0.5 - 0.1 * tail)
                                    faded_color = tuple(int(c * fade) for c in color)
                                    self.strip[led] = faded_color
                            self.strip.show()
                            time.sleep(0.03)
                    for i in indices:
                        if i < self.num_leds:
                            self.strip[i] = (0, 0, 0)
                    self.strip.show()
            self.turn_all_off()
        
    def show_weather(self, weather_status):
        """Display weather data with animated effects."""
        if not weather_status:
            return
        
        print(f"Showing weather animation for: {weather_status}")

    def show_weather(self, weather_status, duration_sec=10, base_brightness=50):
        """Display weather animation for specified duration with adjustable brightness.
        
        Args:
            weather_status (str): Weather condition to display
            duration_sec (float): How long to run animation (default: 10 seconds)
            base_brightness (int): Overall brightness scaling (0-100, default: 100)
        """
        if not weather_status:
            return
        
        weather_status = weather_status.lower()
        end_time = time.time() + duration_sec
        
        while time.time() < end_time:
            if weather_status == 'clear':
                self.sun_animation_loop(end_time, base_brightness)
            elif weather_status == 'clouds':
                self.cloud_animation_loop(end_time, base_brightness)
            elif weather_status == 'rain':
                self.rain_animation_loop(end_time, speed=1.0, drop_chance=0.9, base_brightness=base_brightness)
            elif weather_status == 'drizzle':
                self.rain_animation_loop(end_time, speed=0.5, drop_chance=0.3, base_brightness=base_brightness)
            elif weather_status == 'snow':
                self.snow_animation_loop(end_time, base_brightness=base_brightness)
            elif weather_status == 'thunderstorm':
                self.thunderstorm_animation_loop(end_time, base_brightness)
            elif weather_status in ('mist', 'fog'):
                self.fog_animation_loop(end_time, base_brightness)
            else:
                self.default_animation_loop(end_time, base_brightness)

        self.turn_all_off()

    def sun_animation_loop(self, end_time, base_brightness=100):
        """Continuous sun animation until end_time with brightness scaling"""
        colors = [
            (255, 255, 0),
            (255, 255, 50),
            (255, 255, 20)
        ]
        ray_pattern = [0, 1, 2] * ((self.num_leds // 3) + 1)
        
        brightness_scale = base_brightness / 100.0
        
        while time.time() < end_time:
            cycle_time = time.time()
            cycle_progress = (cycle_time % 2) / 2
            
            core_brightness = int((30 + int(70 * (0.5 + 0.5 * math.sin(cycle_progress * math.pi)))) * brightness_scale)
            
            wave_pos = int(cycle_progress * 3) % 3
            for i in range(self.num_leds):
                dist_from_center = abs(i - self.num_leds//2)
                color_idx = ray_pattern[i]
                wave_effect = (3 - (dist_from_center + wave_pos) % 3) * 30
                brightness = min(100, int((core_brightness + wave_effect) * brightness_scale))
                self.set_led(i, colors[color_idx], brightness)
            
            self.strip.show()
            time.sleep(0.05)

    def cloud_animation_loop(self, end_time, base_brightness=100):
        """Continuous cloud animation until end_time with brightness scaling"""
        cloud_colors = [
            (180, 180, 200),
            (150, 150, 180),
            (120, 120, 150)
        ]
        
        brightness_scale = base_brightness / 100.0
        cloud_positions = deque([random.choice([0, 1, 2]) for _ in range(self.num_leds)])
        last_shift = time.time()
        
        while time.time() < end_time:
            if time.time() - last_shift > 0.2:
                cloud_positions.rotate(1)
                last_shift = time.time()
            
            for i in range(self.num_leds):
                color_idx = cloud_positions[i]
                brightness = int((40 + random.randint(-10, 10)) * brightness_scale)
                self.set_led(i, cloud_colors[color_idx], brightness)
            
            self.strip.show()
            time.sleep(0.05)

    def rain_animation_loop(self, end_time, speed=1.0, drop_chance=0.4, base_brightness=100):
        """Continuous rain animation until end_time with brightness scaling"""
        rain_colors = [
            (100, 0, 50),
            (150, 0, 80),
            (200, 0, 120)
        ]
        brightness_scale = base_brightness / 100.0
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        last_drop_time = time.time()
        
        while time.time() < end_time:
            self.turn_all_off()
            
            if random.random() < drop_chance:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': speed,
                    'color': random.choice(rain_colors),
                    'brightness': int(random.randint(60, 90) * brightness_scale)
                })
            
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds:
                    self.set_led(led_index, drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            
            self.strip.show()
            time.sleep(0.1)

    def snow_animation_loop(self, end_time, speed=0.5, drop_chance=0.3, base_brightness=100):
        """Continuous snow animation until end_time with brightness scaling"""
        snow_colors = [
            (180, 50, 150),
            (220, 80, 200),
            (255, 120, 230)
        ]
        brightness_scale = base_brightness / 100.0
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        last_drop_time = time.time()
        
        while time.time() < end_time:
            self.turn_all_off()
            
            if random.random() < drop_chance:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': speed,
                    'color': random.choice(snow_colors),
                    'brightness': int(random.randint(60, 90) * brightness_scale)
                })
            
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds - 1:
                    self.set_led(led_index + random.randint(0, 1), drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            
            self.strip.show()
            time.sleep(0.1)

    def thunderstorm_animation_loop(self, end_time, base_brightness=100):
        """Continuous thunderstorm animation until end_time with brightness scaling"""
        brightness_scale = base_brightness / 100.0
        last_lightning = time.time()
        rain_colors = [(100, 0, 50), (150, 0, 80), (200, 0, 120)]
        rows = 4
        cols = self.num_leds // rows
        drops = []
        
        while time.time() < end_time:
            self.turn_all_off()
            
            if random.random() < 0.7:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': 1.0,
                    'color': random.choice(rain_colors),
                    'brightness': int(random.randint(60, 90) * brightness_scale)
                })
            
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds:
                    self.set_led(led_index, drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            
            if time.time() - last_lightning > random.uniform(3.0, 8.0):
                last_lightning = time.time()
                for _ in range(random.randint(1, 3)):
                    flash_color = (255, 255, 200)
                    self.fill(flash_color, int(100 * brightness_scale))
                    self.strip.show()
                    time.sleep(0.05)
                    self.turn_all_off()
                    time.sleep(0.05)
            
            self.strip.show()
            time.sleep(0.1)

    def fog_animation_loop(self, end_time, base_brightness=100):
        """Continuous fog animation until end_time with brightness scaling"""
        brightness_scale = base_brightness / 100.0
        fog_color = (150, 150, 180)
        brightness_map = [int(random.randint(10, 30) * brightness_scale) for _ in range(self.num_leds)]
        last_shift = time.time()
        
        while time.time() < end_time:
            if time.time() - last_shift > 0.15:
                brightness_map.insert(0, brightness_map.pop())
                last_shift = time.time()
            
            for i in range(self.num_leds):
                current_brightness = brightness_map[i] + random.randint(-5, 5)
                current_brightness = max(5, min(40, int(current_brightness * brightness_scale)))
                self.set_led(i, fog_color, current_brightness)
            
            self.strip.show()
            time.sleep(0.05)

    def default_animation_loop(self, end_time, base_brightness=100):
        """Continuous default animation until end_time with brightness scaling"""
        brightness_scale = base_brightness / 100.0
        colors = [(100, 100, 100), (150, 150, 150), (200, 200, 200)]
        color_index = 0
        last_change = time.time()
        
        while time.time() < end_time:
            if time.time() - last_change > 0.5:
                color_index = (color_index + 1) % len(colors)
                last_change = time.time()
            
            self.fill(colors[color_index], int(50 * brightness_scale))
            self.strip.show()
            time.sleep(0.05)

