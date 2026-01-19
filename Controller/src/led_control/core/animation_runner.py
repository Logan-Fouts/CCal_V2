import math
import random
import time
from typing import Tuple, Optional
from led_control.core.led_controller import LEDController


class AnimationRunner:
    """Runs various LED animations using LED controller."""

    def __init__(self, led_controller: LEDController):
        self.led = led_controller
        self.num_leds = led_controller.num_leds

    def display_number(
        self, number: int, color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Display a number using the LED controller."""
        self.led.display_number(number, color)
        self.led.show()

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
                    led_index = pixel - i
                    if 0 <= led_index < self.num_leds:
                        self.led.set_pixel(led_index, cloud_colors[0], brightness)
                self.led.show()
                time.sleep(0.5)
                self.turn_all_off()

    def rain_animation_loop(
        self,
        end_time: float,
        speed: float = 1.0,
        drop_chance: float = 0.4,
        brightness: Optional[float] = None,
    ):
        """Run rain animation until end_time."""
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
                drop_brightness = (
                    random.uniform(brightness * 0.6, brightness * 0.9)
                    if brightness
                    else random.uniform(0.6, 0.9)
                )
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
                    self.led.set_pixel(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
                    drops.remove(drop)

            self.led.show()
            time.sleep(0.1)

    def snow_animation_loop(
        self,
        end_time: float,
        speed: float = 0.5,
        drop_chance: float = 0.3,
        brightness: Optional[float] = None,
    ):
        """Run snow animation until end_time."""
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
                drop_brightness = (
                    random.uniform(brightness * 0.6, brightness * 0.9)
                    if brightness
                    else random.uniform(0.6, 0.9)
                )
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
                    self.led.set_pixel(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
                    drops.remove(drop)

            self.led.show()
            time.sleep(0.1)

    def thunderstorm_animation_loop(
        self, end_time: float, brightness: Optional[float] = None
    ):
        """Run thunderstorm animation until end_time."""
        rain_colors = [(0, 128, 255), (0, 0, 255), (0, 128, 255)]
        rows = 4
        cols = self.num_leds // rows
        drops = []
        last_lightning = time.time()

        while time.time() < end_time:
            self.turn_all_off()
            if random.random() < 0.7:
                new_col = random.randint(0, cols - 1)
                drop_brightness = (
                    random.uniform(brightness * 0.6, brightness * 0.9)
                    if brightness
                    else random.uniform(0.6, 0.9)
                )
                drops.append(
                    {
                        "row": 0,
                        "col": new_col,
                        "speed": 1.0,
                        "color": random.choice(rain_colors),
                        "brightness": drop_brightness,
                    }
                )

            for drop in drops[:]:
                led_index = drop["col"] + (int(drop["row"]) * cols)
                if 0 <= led_index < self.num_leds:
                    self.led.set_pixel(led_index, drop["color"], drop["brightness"])
                drop["row"] += drop["speed"]
                if drop["row"] >= rows:
                    drops.remove(drop)

            if time.time() - last_lightning > random.uniform(3.0, 8.0):
                last_lightning = time.time()
                for _ in range(random.randint(1, 3)):
                    flash_color = (255, 255, 200)
                    self.led.fill(flash_color, brightness)
                    self.led.show()
                    time.sleep(0.05)
                    self.turn_all_off()
                    time.sleep(0.05)

            self.led.show()
            time.sleep(0.1)

    def fog_animation_loop(self, end_time: float, brightness: Optional[float] = None):
        """Drifting, gradient fog: multiple moving patches with white/grey gradients."""
        rows = 4
        cols = self.num_leds // rows
        if self.num_leds % rows != 0:
            cols += 1

        # Define several fog patches
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

        min_brightness = brightness * 0.07 if brightness else 0.07
        max_brightness = brightness * 0.18 if brightness else 0.18

        while time.time() < end_time:
            led_map = [min_brightness for _ in range(self.num_leds)]
            color_map = [fog_colors[1] for _ in range(self.num_leds)]

            for patch in patches:
                patch["pos"] = (patch["pos"] + patch["speed"]) % cols
                for col in range(cols):
                    dist = min(abs(col - patch["pos"]), cols - abs(col - patch["pos"]))
                    if dist < patch["width"] / 2:
                        t = dist / (patch["width"] / 2)
                        smooth = 1 - (3 * t * t - 2 * t * t * t)
                        patch_brightness = (
                            min_brightness + (max_brightness - min_brightness) * smooth
                        )

                        row = patch["row"]
                        if row % 2 == 0:
                            led_idx = row * cols + (cols - 1 - col)
                        else:
                            led_idx = row * cols + col

                        if (
                            led_idx < self.num_leds
                            and patch_brightness > led_map[led_idx]
                        ):
                            led_map[led_idx] = patch_brightness
                            color_map[led_idx] = patch["color"]

            for i in range(self.num_leds):
                self.led.set_pixel(i, color_map[i], led_map[i])

            self.led.show()
            time.sleep(0.01)

    def default_animation_loop(
        self, end_time: float, brightness: Optional[float] = None
    ):
        """Run default animation until end_time."""
        colors = [(255, 255, 255), (200, 200, 200), (180, 180, 180)]
        color_index = 0
        last_change = time.time()

        while time.time() < end_time:
            if time.time() - last_change > 0.5:
                color_index = (color_index + 1) % len(colors)
                last_change = time.time()

            self.led.fill(colors[color_index], brightness)
            self.led.show()
            time.sleep(0.05)

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
        """Improved theater chase: moving dots with configurable spacing."""
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

    def wheel(self, pos: int) -> Tuple[int, int, int]:
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        if pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

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

    def flash(self, brightness: Optional[float] = None):
        """Flash all LEDs with white and pastel colors."""
        for _ in range(2):
            self.led.fill((255, 255, 255), brightness)
            self.led.show()
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
                                self.led.set_pixel(led, faded_color, brightness)
                        time.sleep(0.03)

                for i in indices:
                    if i < self.num_leds:
                        self.led.set_pixel(i, (0, 0, 0), brightness)
                self.led.show()

    def run_weather_animation(
        self,
        weather: dict,
        duration_sec: float = 5,
        brightness: Optional[float] = 0.8,
    ):
        """Run appropriate animation based on weather condition."""
        condition = weather.get("weather", [{}])[0].get("main", "").lower()
        end_time = time.time() + duration_sec

        if condition == "clear":
            self.sun_animation_loop(end_time, brightness)
        elif condition == "clouds":
            self.cloud_animation_loop(end_time, brightness)
        elif condition == "rain":
            self.rain_animation_loop(
                end_time, speed=1.0, drop_chance=0.9, brightness=brightness
            )
        elif condition == "drizzle":
            self.rain_animation_loop(
                end_time, speed=0.5, drop_chance=0.2, brightness=brightness
            )
        elif condition == "snow":
            self.snow_animation_loop(end_time, brightness=brightness)
        elif condition == "thunderstorm":
            self.thunderstorm_animation_loop(end_time, brightness)
        elif condition in ("mist", "fog"):
            self.fog_animation_loop(end_time, brightness)
        else:
            pass

        self.turn_all_off()
        temp = weather.get("main", {}).get("temp")
        if temp is not None:
            if temp <= 5:
                color = (0, 128, 255)  # blue for cold
            elif temp >= 25:
                color = (255, 0, 0)  # red for hot
            else:
                color = (255, 255, 255)  # white for normal
            self.display_number(int(round(temp)), color)

    def run_startup_animation(
        self,
        animation_type: int = 0,
        duration_sec: float = 3,
        brightness: Optional[float] = None,
    ):
        """
        Run a startup animation based on the animation_type argument.
        Args:
            animation_type (int): Which animation to run.
                0 - None
                1 - Color wipe (white)
                2 - Theater chase (blue)
                3 - Rainbow cycle
                4 - Flash
            duration_sec (float): How long to run the animation (if applicable).
            brightness (float, optional): LED brightness.
        """

        end_time = time.time() + duration_sec

        if animation_type == 0:
            pass
        elif animation_type == 1:
            self.color_wipe((255, 255, 255), wait=0.03, brightness=brightness)
        elif animation_type == 2:
            self.theater_chase((0, 0, 255), wait=0.05, brightness=brightness)
        elif animation_type == 3:
            self.rainbow_cycle(wait=0.01, brightness=brightness or 1.0)
        elif animation_type == 4:
            self.flash(brightness=brightness)
        else:
            self.default_animation_loop(end_time, brightness)

        self.turn_all_off()

    def update_calendar(self, activityCounts, colors: dict, brightness: float = 0.8):
        """
        Updates LEDs to reflect calendar activity with brightness relative to activity count.
        Args:
            activityCounts (list): List of integers representing activity counts per day.
            colors (dict): Dictionary with 'event' and 'no_events' color tuples.
            brightness (float): Base brightness level for LEDs. Optional.

        This should be used by all activity integrations to display activity.
        """
        if not activityCounts:
            return

        self.event_color = colors.get("event", (0, 255, 0))
        self.none_color = colors.get("no_events", (30, 30, 30))

        max_count = max(activityCounts)
        if max_count == 0:
            for day in range(min(self.num_leds, len(activityCounts))):
                self.led.set_pixel(day, self.none_color, (brightness) * 0.5)
            self.led.show()
            return

        updates = []
        for day in range(min(self.num_leds, len(activityCounts))):
            count = activityCounts[day]
            if count > 0:
                led_brightness = (count / max_count) + 0.05 # Ensure min brightness
                updates.append((day, self.event_color, led_brightness))
            else:
                updates.append((day, self.none_color, brightness * 1))

        for day, color, led_brightness in updates:
            self.led.set_pixel(day, color, led_brightness)
        self.led.show()
