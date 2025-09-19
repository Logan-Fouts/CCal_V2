"""Main entry point for CCal_V2 LED control (rewritten version)."""

import sys
import time
import traceback
from led_control.core.config_manager import ConfigManager
from led_control.core.led_controller import LEDController
from led_control.core.animation_runner import AnimationRunner
from led_control.integrations.github_tracker import GitHubTracker
from led_control.integrations.weather_tracker import WeatherTracker

# Needs to stay like this for sed to patch it in the setup script
USERNAME="username"
CONFIG_PATH = f"/home/{USERNAME}/CCal_V2/config.json"

def safe_get(config, key, default=None, required=False):
    value = config.get(key, default)
    if required and value is None:
        print(f"[ERROR] Required config '{key}' is missing.")
        sys.exit(1)
    return value

def main():
    try:
        # Load configuration
        try:
            config_manager = ConfigManager(CONFIG_PATH)
            config = config_manager.conf
        except Exception as exc:
            print(f"[ERROR] Failed to load config: {exc}")
            sys.exit(1)

        # Extract configuration values
        pin_num = safe_get(config, "PIN_NUM", 18)
        num_leds = safe_get(config, "NUM_LEDS", 28)
        brightness = safe_get(config, "BRIGHTNESS", 0.8)
        startup_animation = safe_get(config, "STARTUP_ANIMATION", "rainbow")
        on_time = safe_get(config, "ON_TIME", 9)
        off_time = safe_get(config, "OFF_TIME", 23)
        github_username = safe_get(config, "GITHUB_USERNAME", required=True)
        github_token = safe_get(config, "GITHUB_TOKEN", required=True)
        weather_api_key = safe_get(config, "OPENWEATHERMAP_API_KEY", required=True)
        weather_lat = safe_get(config, "WEATHER_LAT", required=True)
        weather_lon = safe_get(config, "WEATHER_LON", required=True)
        poll_time = safe_get(config, "POLL_TIME", 90)

        # Initialize hardware and integrations
        led_controller = LEDController(pin_num=pin_num, num_leds=num_leds, brightness=brightness)
        animation_runner = AnimationRunner(led_controller)
        github_tracker = GitHubTracker(github_username, github_token)
        weather_tracker = WeatherTracker(weather_api_key, (weather_lat, weather_lon))

        animation_runner.run_startup_animation(startup_animation, brightness=brightness)

        while True:
            try:
                now_hour = time.localtime().tm_hour
                if on_time != off_time and (brightness == 0 or not (on_time <= now_hour < off_time)):
                    led_controller.turn_all_off()
                    time.sleep(poll_time)
                    continue

                # GitHub events
                try:
                    event_counts = github_tracker.get_event_counts()
                except Exception as exc:
                    print(f"[ERROR] Failed to fetch GitHub events: {exc}")
                    event_counts = []

                # Weather
                try:
                    weather = weather_tracker.get_current_weather()
                except Exception as exc:
                    print(f"[ERROR] Failed to fetch weather: {exc}")
                    weather = None

                animation_runner.turn_all_off()
                animation_runner.run_weather_animation(weather, brightness=brightness)

                # Sleep until next poll
                time.sleep(poll_time)

            except KeyboardInterrupt:
                print("Exiting gracefully.")
                break
            except Exception as exc:
                print(f"[ERROR] Unexpected error in main loop: {exc}")
                traceback.print_exc()
                time.sleep(10)

    except Exception as exc:
        print(f"[FATAL] Unhandled exception: {exc}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()