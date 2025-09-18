"""Animation runner for LED effects in CCal_V2."""

import math
import random
import time


class AnimationRunner:
    """Class to run various LED animations."""

    def __init__(self, led_utils):
        """Initialize AnimationRunner with LED utilities."""
        self.led = led_utils
        self.num_leds = led_utils.num_leds
        self.brightness = led_utils.brightness

    def turn_all_off(self):
        """Turn off all LEDs."""
        self.led.turn_all_off()

    def sun_animation_loop(self, end_time):
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
                self.led.set_led(i, colors[color_idx], self.brightness * led_brightness)
            time.sleep(0.05)

    def cloud_animation_loop(self, end_time, brightness=None):
        """Run cloud animation until end_time."""
        cloud_colors = [(180, 180, 180), (220, 220, 220), (255, 255, 255)]
        cloud = [12, 11, 20, 19, 18, 17]

        self.turn_all_off()
        while time.time() < end_time:
            for i in range(0, 4):
                for pixel in cloud:
                    self.led.set_led(pixel - i, cloud_colors[0], brightness)
                time.sleep(0.5)
                self.turn_all_off()

    def rain_animation_loop(
        self, end_time, speed=1.0, drop_chance=0.4, brightness=None
    ):
        """Run rain animation until end_time."""
        if brightness is None:
            brightness = self.brightness

        rain_colors = [(0, 128, 255), (0, 0, 255)]
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < drop_chance:
                new_col = random.randint(0, cols - 1)
                drop_brightness = random.uniform(brightness * 0.6, brightness * 0.9)
                drops.append(
                    {
                        "row": 0,
                        "col": new_col,
                        "speed": speed,
                        "color": random.choice(rain_colors),
                        "brightness": drop_brightness,
                    }
                )
            for drop in drops[:]:
                led_index = drop["col"] + (int(drop["row"]) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_led(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
                    drops.remove(drop)
            time.sleep(0.1)

    def snow_animation_loop(
        self, end_time, speed=0.5, drop_chance=0.3, brightness=None
    ):
        """Run snow animation until end_time."""
        if brightness is None:
            brightness = self.brightness
        # Use GRB color order to match rain/cloud animations
        snow_colors = [
            (255, 255, 255),  # white (G,R,B)
            (220, 200, 255),  # light blueish (G,R,B)
            (240, 220, 255),  # lighter blueish (G,R,B)
        ]

        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        drops = []
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < drop_chance:
                new_col = random.randint(0, cols - 1)
                drop_brightness = random.uniform(brightness * 0.6, brightness * 0.9)
                drops.append(
                    {
                        "row": 0,
                        "col": new_col,
                        "speed": speed,
                        "color": random.choice(snow_colors),
                        "brightness": drop_brightness,
                    }
                )
            for drop in drops[:]:
                led_index = drop["col"] + (int(drop["row"]) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_led(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
                    drops.remove(drop)
            time.sleep(0.1)

    def thunderstorm_animation_loop(self, end_time, brightness=None):
        """Run thunderstorm animation until end_time."""
        if brightness is None:
            brightness = self.brightness
        rain_colors = [(0, 128, 255), (0, 0, 255), (0, 128, 255)]
        rows = 4
        cols = self.num_leds // rows
        drops = []
        last_lightning = time.time()
        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < 0.7:
                new_col = random.randint(0, cols - 1)
                drops.append(
                    {
                        "row": 0,
                        "col": new_col,
                        "speed": 1.0,
                        "color": random.choice(rain_colors),
                        "brightness": random.uniform(
                            brightness * 0.6, brightness * 0.9
                        ),
                    }
                )
            for drop in drops[:]:
                led_index = drop["col"] + (int(drop["row"]) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_led(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
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
        """Drifting, gradient fog: multiple moving patches with white/grey gradients, like clouds."""
        if brightness is None:
            brightness = self.brightness
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1
        # Define several fog patches, each with its own position, width, color, and speed
        num_patches = 3
        patches = []
        fog_colors = [
            (200, 200, 200),  # light grey
            (180, 180, 180),  # medium grey
            (255, 255, 255),  # white
            (220, 220, 220),  # soft white
        ]
        for _ in range(num_patches):
            patches.append(
                {
                    "row": random.randint(0, rows - 1),
                    "pos": random.uniform(0, cols - 1),
                    "width": random.uniform(cols * 0.4, cols * 0.7),
                    "color": random.choice(fog_colors),
                    "speed": random.uniform(0.02, 0.25) * random.choice([-1, 1]),
                }
            )
        min_brightness = brightness * 0.07
        max_brightness = brightness * 0.18
        while time.time() < end_time:
            # Start with all LEDs at minimum fog
            led_map = [min_brightness for _ in range(self.num_leds)]
            color_map = [fog_colors[1] for _ in range(self.num_leds)]
            for patch in patches:
                patch["pos"] = (patch["pos"] + patch["speed"]) % cols
                for col in range(cols):
                    # Distance from patch center
                    dist = min(abs(col - patch["pos"]), cols - abs(col - patch["pos"]))
                    if dist < patch["width"] / 2:
                        t = dist / (patch["width"] / 2)
                        # Soft gradient edge
                        smooth = 1 - (3 * t * t - 2 * t * t * t)  # smoothstep reversed
                        patch_brightness = (
                            min_brightness + (max_brightness - min_brightness) * smooth
                        )
                        # Map (patch["row"], col) to LED index (serpentine)
                        row = patch["row"]
                        if row % 2 == 0:
                            led_idx = row * cols + (cols - 1 - col)
                        else:
                            led_idx = row * cols + col
                        if led_idx < self.num_leds:
                            # If multiple patches overlap, take the brighter one
                            if patch_brightness > led_map[led_idx]:
                                led_map[led_idx] = patch_brightness
                                color_map[led_idx] = patch["color"]
            for i in range(self.num_leds):
                self.led.set_led(i, color_map[i], led_map[i])
            time.sleep(0.01)

    def default_animation_loop(self, end_time, brightness=None):
        """Run default animation until end_time."""
        if brightness is None:
            brightness = self.brightness
        colors = [(255, 255, 255), (200, 200, 200), (180, 180, 180)]
        color_index = 0
        last_change = time.time()
        while time.time() < end_time:
            if time.time() - last_change > 0.5:
                color_index = (color_index + 1) % len(colors)
                last_change = time.time()
            self.led.fill(colors[color_index], brightness)
            time.sleep(0.05)

    def color_wipe(self, color, wait):
        """Wipe color across display one LED at a time."""
        for i in range(self.num_leds):
            self.led.set_led(i, color, self.brightness)
            time.sleep(wait)
        self.turn_all_off()

    def theater_chase(self, color, wait):
        """Improved theater chase: moving dots with configurable spacing and smooth phase transitions."""
        spacing = 3
        cycles = 15
        for phase in range(spacing):
            for _ in range(cycles):
                for i in range(self.num_leds):
                    if (i + phase) % spacing == 0:
                        self.led.set_led(i, color, self.brightness)
                    else:
                        self.led.set_led(i, (0, 0, 0), self.brightness)
                time.sleep(wait)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        if pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

    def rainbow_cycle(self, wait, brightness=1.0):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256):
            for i in range(self.num_leds):
                pixel_index = (i * 256 // self.num_leds) + j
                color = self.wheel(pixel_index & 255)
                self.led.set_led(i, color, self.brightness * brightness)
            time.sleep(wait)
        self.turn_all_off()

    def flash(self):
        """Flash all LEDs with white and pastel colors."""
        for _ in range(2):
            self.led.fill((255, 255, 255), self.brightness)
            time.sleep(0.10)
            self.turn_all_off()
            time.sleep(0.07)
        pastel_colors = [
            (255, 200, 200),
            (200, 255, 200),
            (200, 200, 255),
            (255, 255, 200),
            (200, 255, 255),
            (255, 200, 255),
        ]
        num_rows = 4
        num_cols = 7
        fade_steps = 4
        for color in pastel_colors:
            for row in range(num_rows):
                if row % 2 == 0:
                    indices = list(range(num_cols * row, num_cols * (row + 1)))
                else:
                    indices = list(
                        range(num_cols * (row + 1) - 1, num_cols * row - 1, -1)
                    )
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
