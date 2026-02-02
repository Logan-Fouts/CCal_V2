"""Main entry point for CCal_V2 LED control (rewritten version)."""

import os
import sys
import time
import traceback
from led_control.core.config_manager import ConfigManager
from led_control.core.led_controller import LEDController
from led_control.core.animation_runner import AnimationRunner
from led_control.core.integration_manager import IntegrationManager
from led_control.integrations.github_tracker import GitHubTracker
from led_control.integrations.weather_tracker import WeatherTracker
from led_control.integrations.strava import StravaTracker
from led_control.integrations.generic_tracker import GenericTracker
from datetime import datetime, timedelta

USERNAME = "lfouts"
CONFIG_PATH = f"/home/{USERNAME}/Daily-Grid/config.json"

# TODO: 
# - Add polltime to webgui
# - Add new services (Uptime Kuma, GitLab, Wiki.js, Vault Warden)
# - More unit tests?
# - Intro animations for api integrations? (e.g. Github, Strava, etc)


def safe_get(config, key, default=None, required=False):
    """Safely get a value from the config, exit if required and missing."""
    value = config.get(key, default)
    if required and value is None:
        print(f"[ERROR] Required config '{key}' is missing.")
        sys.exit(1)
    return value


def load_config():
    """Load and parse configuration file."""
    config_path = CONFIG_PATH
    try:
        config_manager = ConfigManager(config_path)
        return config_manager.conf
    except Exception as exc:
        print(f"[ERROR] Failed to load config from {config_path}: {exc}")
        sys.exit(1)


def extract_config_values(config):
    """Extract all configuration values with defaults."""
    return {
        # Hardware settings
        'pin_num': safe_get(config, "PIN_NUM", 18),
        'num_leds': safe_get(config, "NUM_LEDS", 28), # For future potential expansion
        'brightness': safe_get(config, "BRIGHTNESS", 0.8),
        'startup_animation': safe_get(config, "STARTUP_ANIMATION", 3),
        
        # Schedule settings
        'on_time': safe_get(config, "ON_TIME", 9),
        'off_time': safe_get(config, "OFF_TIME", 22),
        'poll_time': safe_get(config, "POLL_TIME", 90),
        'weather_display_time': safe_get(config, "WEATHER_DISPLAY_TIME", 4),
        
        # API credentials
        'github_username': safe_get(config, "GITHUB_USERNAME", required=False),
        'github_token': safe_get(config, "GITHUB_TOKEN", required=False),
        'weather_api_key': safe_get(config, "OPENWEATHERMAP_API_KEY", required=True),
        'weather_lat': safe_get(config, "WEATHER_LAT", required=True),
        'weather_lon': safe_get(config, "WEATHER_LON", required=True),
        'strava_client_id': safe_get(config, "STRAVA_ID", required=False),
        'strava_client_secret': safe_get(config, "STRAVA_SECRET", required=False),
        
        # Display colors
        'github_no_events_color': safe_get(config, "GITHUB_NO_EVENTS_COLOR", [30, 30, 30]),
        'github_event_color': safe_get(config, "GITHUB_EVENT_COLOR", [0, 255, 0]),

        'strava_events_color': safe_get(config, "STRAVA_EVENTS_COLOR", [255, 165, 0]),
        'strava_no_events_color': safe_get(config, "STRAVA_NO_EVENTS_COLOR", [30, 30, 30]),
    }


def setup_integrations(cfg, animation_runner):
    """Initialize all integration trackers and manager."""
    trackers = []

    if cfg['github_username'] and cfg['github_token']:
        colors = {
            "event": cfg['github_event_color'],
            "no_events": cfg['github_no_events_color']
        }
        github_tracker = GitHubTracker(cfg['github_username'], cfg['github_token'], colors=colors)
        trackers.append(github_tracker)
    
    if cfg['strava_client_id'] and cfg['strava_client_secret']:
        colors = {
            "event": cfg['strava_events_color'],
            "no_events": cfg['strava_no_events_color']
        }
        strava_tracker = StravaTracker(
            client_id=cfg['strava_client_id'], 
            client_secret=cfg['strava_client_secret'],
            num_days=cfg['num_leds'],
            colors=colors
        )
        trackers.append(strava_tracker)

    if cfg['weather_api_key'] and cfg['weather_lat'] and cfg['weather_lon']:
        weather_tracker = WeatherTracker(
            cfg['weather_api_key'], 
            (cfg['weather_lat'], cfg['weather_lon'])
        )
    
    # For each file in the CustomTrackers directory, create a GenericTracker integration
    custom_trackers_dir = f"/home/{USERNAME}/Daily-Grid/CustomTrackers"
    for filename in os.listdir(custom_trackers_dir):
        if filename.endswith(".json"):
            tracker_path = os.path.join(custom_trackers_dir, filename)
            try:
                generic_tracker = GenericTracker(tracker_path)
                trackers.append(generic_tracker)
            except Exception as exc:
                print(f"[ERROR] Failed to load GenericTracker from {tracker_path}: {exc}")
    
    return IntegrationManager(
        animation_runner=animation_runner,
        trackers=trackers,
        weather_tracker=weather_tracker
    )


def main():
    """Main program loop for LED control."""
    try:
        config = load_config()
        cfg = extract_config_values(config)

        led_controller = LEDController(
            pin_num=cfg['pin_num'], 
            num_leds=cfg['num_leds'], 
            brightness=cfg['brightness']
        )
        animation_runner = AnimationRunner(led_controller)
        
        integration_manager = setup_integrations(cfg, animation_runner)

        animation_runner.run_startup_animation(
            cfg['startup_animation'], 
            brightness=cfg['brightness']
        )

        # Main loop
        while True:
            try:
                now_hour = time.localtime().tm_hour
                if (cfg['on_time'] != cfg['off_time'] and 
                    (cfg['brightness'] == 0 or not (cfg['on_time'] <= now_hour < cfg['off_time']))):
                    led_controller.turn_all_off()

                    # Compute seconds until next on_time and sleep that long
                    now = datetime.now()
                    target = now.replace(hour=cfg['on_time'], minute=0, second=0, microsecond=0)
                    if target <= now:
                        target += timedelta(days=1)
                    sleep_seconds = (target - now).total_seconds()
                    print(f"[INFO] Off-period. Sleeping for {int(sleep_seconds)} seconds until hour {cfg['on_time']}.")
                    time.sleep(sleep_seconds)

                    continue

                integration_manager.run_integration_cycle(
                    brightness=cfg['brightness'],
                    poll_time=cfg['poll_time'],
                    weather_display_time=cfg['weather_display_time']
                )

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
