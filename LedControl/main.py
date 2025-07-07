import time
from led_utils import LED_UTILS
from github_tracker import GITHUB_TRACKER
from config_manager import CONFIG_MANAGER
from weather_tracker import WEATHER_TRACKER

def main():
    poll_time, pin_num, num_days, none_color, event_color = 90, 18, 28, (255, 255, 255), (255, 0, 0)

    # config_file = "/home/logan/Code/CCal_V2/config.json" 
    config_file = "/home/ccalv2/CCal_V2/config.json" 
    config_manager = CONFIG_MANAGER(config_file)
    config = config_manager.load_config()
    
    leds = LED_UTILS(num_days, config.get('STARTUP_ANIMATION', 0), none_color, event_color, pin_num)
    gh_tracker = GITHUB_TRACKER(num_days)

    weather_tracker = WEATHER_TRACKER(config.get('OPENWEATHERMAP_API_KEY'), config.get('WEATHER_LAT', 40.71), config.get('WEATHER_LON', -74.01))


    while True:
        event_counts = gh_tracker.fetch_github_events()
        leds.update_leds(event_counts)
        if gh_tracker.print_new_events():
            leds.flash()
    
        end_time = time.time() + poll_time
        while time.time() < end_time:
            leds.update_leds(event_counts)
            time.sleep(55)
            leds.show_weather(weather_tracker.get_weather(), duration_sec=5, base_brightness=30)

if __name__ == "__main__":
    main()
