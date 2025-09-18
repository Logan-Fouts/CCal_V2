"""
Demo script for LedUtils and AnimationRunner in CCal_V2.
Shows off number display, color fills, and all animations.
"""
import time
from led_utils import LedUtils


def demo_numbers(leds):
    print("Displaying numbers 0-10...")
    for n in range(11):
        leds.turn_all_off()
        leds.display_number(n)
        time.sleep(0.7)
    leds.turn_all_off()
    time.sleep(0.5)


def demo_color_fills(leds):
    print("Showing color fills...")
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (0, 255, 255), (255, 0, 255),
        (255, 255, 255), (127, 127, 127), (0, 0, 0)
    ]
    for color in colors:
        leds.fill(color)
        time.sleep(0.5)
    leds.turn_all_off()
    time.sleep(0.5)


def demo_animations(leds):
    print("Running all animations...")
    anim = leds.anim
    now = time.time()
    anims = [
        (anim.sun_animation_loop, 2),
        (anim.cloud_animation_loop, 2),
        (anim.rain_animation_loop, 2),
        (anim.snow_animation_loop, 2),
        (anim.thunderstorm_animation_loop, 2),
        (anim.fog_animation_loop, 2),
        (anim.default_animation_loop, 2),
        (lambda et: anim.color_wipe((0,255,0), 0.05), 1),
        (lambda et: anim.theater_chase((255,0,255), 0.07), 1),
        (lambda et: anim.flash(), 1),
    ]
    for func, duration in anims:
        print(f"Running {func.__name__ if hasattr(func, '__name__') else func}...")
        leds.turn_all_off()
        func(time.time() + duration)
        leds.turn_all_off()
        time.sleep(0.5)


def main():
    leds = LedUtils(num_days=28, brightness=0.9)
    demo_numbers(leds)
    demo_color_fills(leds)
    demo_animations(leds)
    leds.turn_all_off()
    print("Demo complete.")


if __name__ == "__main__":
    main()
