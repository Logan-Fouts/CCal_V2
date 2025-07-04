import time
from led_utils import LED_UTILS
from github_tracker import GITHUB_TRACKER
from config_manager import CONFIG_MANAGER

def main():
    pin_num, num_days, none_color, event_color = 18, 28, (255, 255, 255), (255, 0, 0)
    
    config_manager = CONFIG_MANAGER()
    config = config_manager.load_config()
    
    leds = LED_UTILS(num_days, config.get('STARTUP_ANIMATION', 0), none_color, event_color, pin_num)
    gh_tracker = GITHUB_TRACKER(num_days)
    
    while True:
        event_counts = gh_tracker.fetch_github_events()
        leds.update_leds(event_counts)
        if gh_tracker.print_new_events():
            leds.flash()
            leds.update_leds(event_counts)
        time.sleep(60)  # 1 minute

if __name__ == "__main__":
    main()
