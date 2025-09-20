import time
from led_control.core.led_controller import LEDController
from led_control.core.animation_runner import AnimationRunner

NUM_LEDS = 28
led_controller = LEDController()
runner = AnimationRunner(led_controller)

def run_all_animations(brightness):
    print(f"Running all animations at brightness {brightness}")
    duration = 10

    # Color wipe
    print("Color wipe")
    runner.color_wipe((255, 0, 0), wait=0.03, brightness=brightness)
    # Theater chase
    print("Theater chase")
    runner.theater_chase((0, 255, 0), wait=0.05, brightness=brightness)
    # Rainbow cycle
    print("Rainbow cycle")
    runner.rainbow_cycle(wait=0.01, brightness=brightness)
    # Flash
    print("Flash")
    runner.flash(brightness=brightness)
    # Weather animation (simulate each type)
    print("Weather: clear")
    runner.run_weather_animation({"weather": [{"main": "Clear"}]}, duration_sec=2, brightness=brightness)
    print("Weather: clouds")
    runner.run_weather_animation({"weather": [{"main": "Clouds"}]}, duration_sec=2, brightness=brightness)
    print("Weather: rain")
    runner.run_weather_animation({"weather": [{"main": "Rain"}]}, duration_sec=2, brightness=brightness)
    print("Weather: drizzle")
    runner.run_weather_animation({"weather": [{"main": "Drizzle"}]}, duration_sec=2, brightness=brightness)
    print("Weather: snow")
    runner.run_weather_animation({"weather": [{"main": "Snow"}]}, duration_sec=2, brightness=brightness)
    print("Weather: thunderstorm")
    runner.run_weather_animation({"weather": [{"main": "Thunderstorm"}]}, duration_sec=2, brightness=brightness)
    print("Weather: fog")
    runner.run_weather_animation({"weather": [{"main": "Fog"}]}, duration_sec=2, brightness=brightness)
    print("Weather: unknown")
    runner.run_weather_animation({"weather": [{"main": "Unknown"}]}, duration_sec=2, brightness=brightness)

def count_demo(brightness):
    print(f"Counting from 0 to 100 at brightness {brightness}")
    for i in range(101):
        runner.display_number(i)
        time.sleep(0.2)
        runner.turn_all_off()
    runner.turn_all_off()

if __name__ == "__main__":
    for b in [0.1, 0.5, 1.0]:
        run_all_animations(b)
        count_demo(b)
    print("Demo complete.")
