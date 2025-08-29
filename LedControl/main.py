import time
import sys
import traceback
from led_utils import LED_UTILS
from github_tracker import GITHUB_TRACKER
from config_manager import CONFIG_MANAGER
from weather_tracker import WEATHER_TRACKER

# TODO: Remove hardcoded username
USERNAME="ccal"

def safe_get(config, key, default=None, required=False):
    value = config.get(key, default)
    if required and value is None:
        print(f"[ERROR] Required config '{key}' is missing.")
        sys.exit(1)
    return value

def main():
    try:
        # Load configuration
        config_file = f"/home/{USERNAME}/CCal_V2/config.json"
        try:
            config_manager = CONFIG_MANAGER(config_file)
            config = config_manager.load_config()
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            sys.exit(1)

        # Extract configuration values with defaults
        poll_time = safe_get(config, 'POLL_TIME', 90)
        pin_num = safe_get(config, 'PIN_NUM', 18)
        num_days = safe_get(config, 'NUM_DAYS', 28)
        none_color = tuple(safe_get(config, 'NONE_COLOR', [255, 255, 255]))
        event_color = tuple(safe_get(config, 'EVENT_COLOR', [255, 0, 0]))
        brightness = safe_get(config, 'BRIGHTNESS', 100)

        # Required for weather
        weather_api_key = safe_get(config, 'OPENWEATHERMAP_API_KEY', required=True)
        weather_lat = safe_get(config, 'WEATHER_LAT', required=True)
        weather_lon = safe_get(config, 'WEATHER_LON', required=True)

        # Initialize components
        try:
            leds = LED_UTILS(num_days, config.get('STARTUP_ANIMATION', True), none_color, event_color, pin_num, brightness)
        except Exception as e:
            print(f"[ERROR] Failed to initialize LED_UTILS: {e}")
            sys.exit(1)
        try:
            gh_tracker = GITHUB_TRACKER(num_days)
        except Exception as e:
            print(f"[ERROR] Failed to initialize GITHUB_TRACKER: {e}")
            sys.exit(1)
        try:
            weather_tracker = WEATHER_TRACKER(weather_api_key, weather_lat, weather_lon)
        except Exception as e:
            print(f"[ERROR] Failed to initialize WEATHER_TRACKER: {e}")
            sys.exit(1)

        while True:
            try:
                start_time = time.time()
                try:
                    event_counts = gh_tracker.fetch_github_events()
                except Exception as e:
                    print(f"[ERROR] Failed to fetch GitHub events: {e}")
                    event_counts = []
                try:
                    leds.update_leds(event_counts)
                except Exception as e:
                    print(f"[ERROR] Failed to update LEDs: {e}")
                try:
                    weather_status = weather_tracker.get_weather()
                except Exception as e:
                    print(f"[ERROR] Failed to fetch weather: {e}")
                    weather_status = None

                elapsed = 0
                while elapsed < poll_time:
                    time.sleep(60)
                    try:
                        if weather_status is not None:
                            leds.show_weather(weather_status, brightness, duration_sec=5)
                    except Exception as e:
                        print(f"[ERROR] Failed to show weather on LEDs: {e}")
                    try:
                        leds.update_leds(event_counts)
                    except Exception as e:
                        print(f"[ERROR] Failed to update LEDs: {e}")
                    elapsed = time.time() - start_time
            except KeyboardInterrupt:
                print("Exiting gracefully.")
                break
            except Exception as e:
                print(f"[ERROR] Unexpected error in main loop: {e}")
                traceback.print_exc()
                time.sleep(10)  # Prevent rapid crash loop

    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
