import time
from led_utils import LED_UTILS
from github_tracker import GITHUB_TRACKER
from config_manager import CONFIG_MANAGER
from weather_tracker import WEATHER_TRACKER

def main():
    # Load configuration
    config_file = "/home/ccalv2/CCal_V2/config.json"
    config_manager = CONFIG_MANAGER(config_file)
    config = config_manager.load_config()

    # Extract configuration values with defaults
    poll_time = config.get('POLL_TIME', 90)
    pin_num = config.get('PIN_NUM', 18)
    num_days = config.get('NUM_DAYS', 28)
    none_color = tuple(config.get('NONE_COLOR', [255, 255, 255]))
    event_color = tuple(config.get('EVENT_COLOR', [255, 0, 0]))
    brightness = config.get('BRIGHTNESS', 100)

    # Initialize components
    leds = LED_UTILS(num_days, config.get('STARTUP_ANIMATION', True), none_color, event_color, pin_num, brightness)
    gh_tracker = GITHUB_TRACKER(num_days)
    weather_tracker = WEATHER_TRACKER(
        config.get('OPENWEATHERMAP_API_KEY'),
        config.get('WEATHER_LAT'),
        config.get('WEATHER_LON')
    )

    while True:
        start_time = time.time()
        event_counts = gh_tracker.fetch_github_events()
        leds.update_leds(event_counts)
        weather_status = weather_tracker.get_weather()

        elapsed = 0
        while elapsed < poll_time:
            time.sleep(60)
            leds.show_weather(weather_status, brightness, duration_sec=5)
            leds.update_leds(event_counts)
            elapsed = time.time() - start_time

if __name__ == "__main__":
    main()
