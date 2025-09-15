"""Main entry point for CCal_V2 LED control."""

import time
import sys
import traceback
from led_utils import LedUtils
from github_tracker import GithubTracker
from config_manager import ConfigManager
from weather_tracker import WeatherTracker

USERNAME="username"


def safe_get(config, key, default=None, required=False):
    """Safely get a value from the config dictionary."""
    value = config.get(key, default)
    if required and value is None:
        print(f"[ERROR] Required config '{key}' is missing.")
        sys.exit(1)
    return value


def main():
    """Main loop for running the LED control logic."""
    try:
        # Load configuration
        config_file = f"/home/{USERNAME}/CCal_V2/config.json"
        try:
            config_manager = ConfigManager(config_file)
            config = config_manager.load_config()
        except Exception as exc:
            print(f"[ERROR] Failed to load config: {exc}")
            sys.exit(1)

        # Extract configuration values with defaults
        poll_time = safe_get(config, "POLL_TIME", 90)
        pin_num = safe_get(config, "PIN_NUM", 18)
        num_days = safe_get(config, "NUM_DAYS", 28)
        none_color = tuple(safe_get(config, "NONE_COLOR", [255, 255, 255]))
        event_color = tuple(safe_get(config, "EVENT_COLOR", [0, 255, 0]))
        brightness = safe_get(config, "BRIGHTNESS", 0.8)
        on_time = safe_get(config, "ON_TIME", 9)
        off_time = safe_get(config, "OFF_TIME", 23)

        # Required for weather
        weather_api_key = safe_get(config, "OPENWEATHERMAP_API_KEY", required=True)
        weather_lat = safe_get(config, "WEATHER_LAT", required=True)
        weather_lon = safe_get(config, "WEATHER_LON", required=True)

        # Initialize components
        try:
            leds = LedUtils(
                num_days,
                config.get("STARTUP_ANIMATION", True),
                none_color,
                event_color,
                pin_num,
                brightness,
            )
        except Exception as exc:
            print(f"[ERROR] Failed to initialize LED_UTILS: {exc}")
            sys.exit(1)
        try:
            gh_tracker = GithubTracker(num_days)
        except Exception as exc:
            print(f"[ERROR] Failed to initialize GithubTracker: {exc}")
            sys.exit(1)
        try:
            weather_tracker = WeatherTracker(weather_api_key, weather_lat, weather_lon)
        except Exception as exc:
            print(f"[ERROR] Failed to initialize WEATHER_TRACKER: {exc}")
            sys.exit(1)

        while True:
            try:
                start_time = time.time()
                # If brightness is 0, skip all LED updates and just sleep
                if brightness == 0:
                    time.sleep(poll_time)
                    continue
                try:
                    event_counts = gh_tracker.fetch_github_events()
                except Exception as exc:
                    print(f"[ERROR] Failed to fetch GitHub events: {exc}")
                    event_counts = []
                try:
                    leds.update_leds(event_counts)
                except Exception as exc:
                    print(f"[ERROR] Failed to update LEDs: {exc}")
                try:
                    weather_status = weather_tracker.get_weather()
                except Exception as exc:
                    print(f"[ERROR] Failed to fetch weather: {exc}")
                    weather_status = None

                elapsed = 0
                while elapsed < poll_time:
                    time.sleep(60)
                    if brightness == 0 or not (
                        on_time <= time.localtime().tm_hour < off_time
                    ):
                        elapsed = time.time() - start_time
                        continue
                    try:
                        if weather_status is not None:
                            leds.show_weather(
                                weather_status, brightness, duration_sec=5
                            )
                    except Exception as exc:
                        print(f"[ERROR] Failed to show weather on LEDs: {exc}")
                    try:
                        leds.update_leds(event_counts)
                    except Exception as exc:
                        print(f"[ERROR] Failed to update LEDs: {exc}")
                    elapsed = time.time() - start_time
            except KeyboardInterrupt:
                print("Exiting gracefully.")
                break
            except Exception as exc:
                print(f"[ERROR] Unexpected error in main loop: {exc}")
                traceback.print_exc()
                time.sleep(10)  # Prevent rapid crash loop

    except Exception as exc:
        print(f"[FATAL] Unhandled exception: {exc}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
