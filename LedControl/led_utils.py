from rpi_ws281x import PixelStrip, Color
import time
import random

class LED_UTILS:
    def __init__(self, num_days=7, animation=3, none_color=(255, 0, 0), event_color=(0, 255, 0), pin_num=18):
        self.num_leds = num_days
        self.animation = animation
        self.none_color = none_color
        self.event_color = event_color
        
        # LED strip configuration:
        LED_COUNT = self.num_leds
        LED_PIN = pin_num
        LED_FREQ_HZ = 800000
        LED_DMA = 10
        LED_BRIGHTNESS = 255
        LED_INVERT = False
        LED_CHANNEL = 0

        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.turn_all_off()
        self.startup_animation()
        self.turn_all_off()

    def set_led(self, led_index, color, brightness=50):
        r, g, b = color
        brightness = max(0, min(100, brightness))
        r = int(r * brightness / 100)
        g = int(g * brightness / 100)
        b = int(b * brightness / 100)
        self.strip.setPixelColor(led_index, Color(r, g, b))
        self.strip.show()

    def fill(self, color, brightness=50):
        for i in range(self.num_leds):
            self.set_led(i, color, brightness)

    def turn_all_off(self):
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, Color(0, 0, 0))
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
                    brightness = 1 + int(99 * (count / max_count))
                self.set_led(day, self.event_color, brightness)
            else:
                self.set_led(day, self.none_color, 5)
            time.sleep(0.05)

    def startup_animation(self):
        if self.animation == 0:
            pass
        elif self.animation == 1:
            # Sequential pop
            for i in range(self.num_leds):
                _, color_rgb = self.colors[i % len(self.colors)]
                self.set_led(i, color_rgb, 30)
                time.sleep_ms(50)
                self.set_led(i, self.colors[len(self.colors) - 1][1], 0)
        elif self.animation == 2:
            # Color wave
            for _ in range(2):
                for _, color_rgb in self.colors:
                    for i in range(self.num_leds):
                        self.set_led(i, color_rgb, 30)
                        if i > 0:
                            self.set_led(i-1, color_rgb, 15)
                        time.sleep_ms(100)
                    self.turn_all_off()
        elif self.animation == 3:
            # Sparkle
            for _ in range(25):
                idx = random.randint(0, self.num_leds-1)
                _, color_rgb = random.choice(self.colors)
                self.set_led(idx, color_rgb, 30)
                time.sleep_ms(100)
                self.set_led(idx, self.colors[len(self.colors) - 1][1], 0)
        elif self.animation == 4:
            # Rainbow wave
            for j in range(256):  # Cycle through all colors
                for i in range(self.num_leds):
                    # Each LED gets a slightly offset hue
                    hue = ((i * 256 // self.num_leds) + j) % 256
                    color_rgb = self.hsv_to_rgb(hue / 255, 1.0, 1.0)
                    self.set_led(i, color_rgb, 30)
                time.sleep_ms(20)
        elif self.animation == 5:
            # Fire effect
            for _ in range(100):  # Run for 100 cycles
                for i in range(self.num_leds):
                    # Random flicker between red, orange, and yellow
                    flicker = random.randint(0, 50)
                    r = 255 - flicker
                    g = 50 + flicker
                    b = 0
                    self.set_led(i, (r, g, b), 30)
                time.sleep_ms(100)
        elif self.animation == 6:
            # Bouncing ball
            ball_pos = 0
            ball_dir = 1
            ball_color = (255, 0, 0)  # Red ball

            for _ in range(100):  # Run for 100 steps
                self.turn_all_off()
                self.set_led(ball_pos, ball_color, 30)
                
                ball_pos += ball_dir
                if ball_pos >= self.num_leds - 1 or ball_pos <= 0:
                    ball_dir *= -1  # Reverse direction
                
                time.sleep_ms(50)
        elif self.animation == 7:
            # Police lights
            for _ in range(20):  # Flash 20 times
                # Red half
                for i in range(self.num_leds // 2):
                    self.set_led(i, (255, 0, 0), 30)
                # Blue half
                for i in range(self.num_leds // 2, self.num_leds):
                    self.set_led(i, (0, 0, 255), 30)
                time.sleep_ms(200)
                
                # Swap sides
                for i in range(self.num_leds // 2):
                    self.set_led(i, (0, 0, 255), 30)
                for i in range(self.num_leds // 2, self.num_leds):
                    self.set_led(i, (255, 0, 0), 30)
                time.sleep_ms(200)
        elif self.animation == 8:
            # Meteor rain
            for _ in range(5):  # Repeat 5 times
                for i in range(self.num_leds + 5):
                    self.turn_all_off()
                    # Draw meteor with fading tail
                    for j in range(5):
                        if i - j >= 0 and i - j < self.num_leds:
                            brightness = 30 - (j * 6)
                            if brightness > 0:
                                self.set_led(i - j, (255, 255, 255), brightness)
                    time.sleep_ms(50)
        elif self.animation == 9:
            # Color wipe (fill and clear)
            for color in self.colors:
                _, color_rgb = color
                # Fill
                for i in range(self.num_leds):
                    self.set_led(i, color_rgb, 30)
                    time.sleep_ms(30)
                # Clear
                for i in range(self.num_leds):
                    self.set_led(i, (0, 0, 0), 0)
                    time.sleep_ms(30)
        else:
            # Smooth fill to white
            for bri in range(0, 30, 1):
                self.fill(self.colors[7][1], bri)
                time.sleep_ms(25)
    

        self.turn_all_off()

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB (h=0-1, s=0-1, v=0-1)."""
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1:
            return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2:
            return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3:
            return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4:
            return (int(t * 255), int(p * 255), int(v * 255))
        if i == 5:
            return (int(v * 255), int(p * 255), int(q * 255))
