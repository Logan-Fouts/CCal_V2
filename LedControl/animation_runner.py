from collections import deque
import math
import random
import time

class AnimationRunner:
    def __init__(self, led_utils):
        self.led = led_utils
        self.num_leds = led_utils.num_leds
        self.brightness = led_utils.brightness

    def turn_all_off(self):
        self.led.turn_all_off()

    def sun_animation_loop(self, end_time):
        colors = [
            (255, 255, 0),
            (255, 255, 50),
            (255, 255, 20)
        ]
        ray_pattern = [0, 1, 2] * ((self.num_leds // 3) + 1)
        while time.time() < end_time:
            cycle_time = time.time()
            cycle_progress = (cycle_time % 2) / 2
            core_brightness = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(cycle_progress * math.pi))
            wave_pos = int(cycle_progress * 3) % 3
            for i in range(self.num_leds):
                dist_from_center = abs(i - self.num_leds//2)
                color_idx = ray_pattern[i]
                wave_effect = (3 - (dist_from_center + wave_pos) % 3) * 0.3
                led_brightness = min(1.0, core_brightness + wave_effect)
                self.led.set_led(i, colors[color_idx], self.brightness * led_brightness)
            time.sleep(0.05)

    def cloud_animation_loop(self, end_time, brightness=None):
        if brightness is None:
            brightness = self.brightness
        cloud_colors = [
            (180, 180, 200),
            (150, 150, 180),
            (120, 120, 150)
        ]
        cloud = [12, 11, 20, 19, 18, 17]

        self.turn_all_off()
        while time.time() < end_time:
            for i in range(0, 4):
                for pixel in cloud:
                    self.led.set_led(pixel - i, cloud_colors[0], brightness)
                time.sleep(0.5)
                self.turn_all_off()

    def rain_animation_loop(self, end_time, speed=1.0, drop_chance=0.4, brightness=None):
        if brightness is None:
            brightness = self.brightness
        rain_colors = [
            (100, 0, 50),
            (150, 0, 80),
            (200, 0, 120)
        ]
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < drop_chance:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': speed,
                    'color': random.choice(rain_colors),
                    'brightness': random.randint(int(brightness*0.6), int(brightness*0.9))
                })
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_led(led_index, drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            time.sleep(0.1)

    def snow_animation_loop(self, end_time, speed=0.5, drop_chance=0.3, brightness=None):
        if brightness is None:
            brightness = self.brightness
        snow_colors = [
            (180, 50, 150),
            (220, 80, 200),
            (255, 120, 230)
        ]
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < drop_chance:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': speed,
                    'color': random.choice(snow_colors),
                    'brightness': random.randint(int(brightness*0.6), int(brightness*0.9))
                })
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds - 1:
                    self.led.set_led(led_index + random.randint(0, 1), drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            time.sleep(0.1)

    def thunderstorm_animation_loop(self, end_time, brightness=None):
        if brightness is None:
            brightness = self.brightness
        rain_colors = [(100, 0, 50), (150, 0, 80), (200, 0, 120)]
        rows = 4
        cols = self.num_leds // rows
        drops = []
        last_lightning = time.time()
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < 0.7:
                new_col = random.randint(0, cols-1)
                drops.append({
                    'row': 0,
                    'col': new_col,
                    'speed': 1.0,
                    'color': random.choice(rain_colors),
                    'brightness': random.randint(int(brightness*0.6), int(brightness*0.9))
                })
            for drop in drops[:]:
                led_index = drop['col'] + (int(drop['row']) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_led(led_index, drop['color'], drop['brightness'])
                drop['row'] += drop['speed']
                if drop['row'] >= rows:
                    drops.remove(drop)
            if time.time() - last_lightning > random.uniform(3.0, 8.0):
                last_lightning = time.time()
                for _ in range(random.randint(1, 3)):
                    flash_color = (255, 255, 200)
                    self.led.fill(flash_color, brightness)
                    time.sleep(0.05)
                    self.turn_all_off()
                    time.sleep(0.05)
            time.sleep(0.1)

    def fog_animation_loop(self, end_time, brightness=None):
        if brightness is None:
            brightness = self.brightness
        fog_color = (150, 150, 180)
        brightness_map = [random.randint(int(brightness*0.1), int(brightness*0.3)) for _ in range(self.num_leds)]
        last_shift = time.time()
        while time.time() < end_time:
            if time.time() - last_shift > 0.15:
                brightness_map.insert(0, brightness_map.pop())
                last_shift = time.time()
            for i in range(self.num_leds):
                current_brightness = brightness_map[i] + random.randint(-5, 5)
                current_brightness = max(int(brightness*0.05), min(int(brightness*0.4), current_brightness))
                self.led.set_led(i, fog_color, current_brightness)
            time.sleep(0.05)

    def default_animation_loop(self, end_time, brightness=None):
        if brightness is None:
            brightness = self.brightness
        colors = [(100, 100, 100), (150, 150, 150), (200, 200, 200)]
        color_index = 0
        last_change = time.time()
        while time.time() < end_time:
            if time.time() - last_change > 0.5:
                color_index = (color_index + 1) % len(colors)
                last_change = time.time()
            self.led.fill(colors[color_index], brightness)
            time.sleep(0.05)

    def color_wipe(self, color, wait):
        for i in range(self.num_leds):
            self.led.set_led(i, color, self.brightness)
            time.sleep(wait)
        self.turn_all_off()

    def theater_chase(self, color, wait):
        for q in range(10):
            for i in range(0, self.num_leds, 3):
                self.led.set_led(i, color, self.brightness)
            time.sleep(wait)
            for i in range(0, self.num_leds, 3):
                self.led.set_led(i, (0, 0, 0), self.brightness)

    def wheel(self, pos):
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        elif pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        else:
            pos -= 170
            return (0, int(pos * 3), int(255 - pos * 3))

    def rainbow_cycle(self, wait, brightness=1.0):
        for j in range(256):
            for i in range(self.num_leds):
                pixel_index = (i * 256 // self.num_leds) + j
                color = self.wheel(pixel_index & 255)
                self.led.set_led(i, color, self.brightness * brightness)
            time.sleep(wait)
        self.turn_all_off()

    def flash(self):
        for _ in range(2):
            self.led.fill((180, 180, 180), self.brightness)
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
                                self.led.set_led(led, faded_color, self.brightness)
                        time.sleep(0.03)
                for i in indices:
                    if i < self.num_leds:
                        self.led.set_led(i, (0, 0, 0), self.brightness)
