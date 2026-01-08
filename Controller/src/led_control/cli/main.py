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
from led_control.integrations.spotify import SpotifyTracker
from led_control.integrations.strava import StravaTracker

USERNAME = "username"
CONFIG_PATH = f"/home/{USERNAME}/CCal_V2/config.json"


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
        'num_leds': safe_get(config, "NUM_LEDS", 28),
        'brightness': safe_get(config, "BRIGHTNESS", 0.8),
        'startup_animation': safe_get(config, "STARTUP_ANIMATION", 3),
        
        # Schedule settings
        'on_time': safe_get(config, "ON_TIME", 9),
        'off_time': safe_get(config, "OFF_TIME", 23),
        'poll_time': safe_get(config, "POLL_TIME", 30),
        
        # API credentials
        'github_username': safe_get(config, "GITHUB_USERNAME", required=False),
        'github_token': safe_get(config, "GITHUB_TOKEN", required=False),
        'weather_api_key': safe_get(config, "OPENWEATHERMAP_API_KEY", required=True),
        'weather_lat': safe_get(config, "WEATHER_LAT", required=True),
        'weather_lon': safe_get(config, "WEATHER_LON", required=True),
        'spotify_client_id': safe_get(config, "SPOT_ID", required=False),
        'spotify_client_secret': safe_get(config, "SPOT_SECRET", required=False),
        'strava_client_id': safe_get(config, "STRAVA_ID", required=False),
        'strava_client_secret': safe_get(config, "STRAVA_SECRET", required=False),
        
        # Display colors
        'no_events_color': safe_get(config, "NO_EVENTS_COLOR", [30, 30, 30]),
        'event_color': safe_get(config, "EVENT_COLOR", [0, 255, 0]),
    }


def setup_integrations(cfg, animation_runner):
    """Initialize all integration trackers and manager."""
    # Initialize trackers (only if credentials provided)
    github_tracker = None
    if cfg['github_username'] and cfg['github_token']:
        github_tracker = GitHubTracker(cfg['github_username'], cfg['github_token'])
    
    strava_tracker = None  
    if cfg['strava_client_id'] and cfg['strava_client_secret']:
        strava_tracker = StravaTracker(
            client_id=cfg['strava_client_id'], 
            client_secret=cfg['strava_client_secret'],
            num_days=cfg.get['num_days', 28]
        )
    
    weather_tracker = WeatherTracker(
        cfg['weather_api_key'], 
        (cfg['weather_lat'], cfg['weather_lon'])
    )
    
    spotify_tracker = None
    if cfg['spotify_client_id'] and cfg['spotify_client_secret']:
        spotify_tracker = SpotifyTracker(
            client_id=cfg['spotify_client_id'], 
            client_secret=cfg['spotify_client_secret']
        )
    
    # Initialize integration manager
    return IntegrationManager(
        animation_runner=animation_runner,
        github_tracker=github_tracker,
        strava_tracker=strava_tracker,
        weather_tracker=weather_tracker,
        spotify_tracker=spotify_tracker
    )


def main():
    """Main program loop for LED control."""
    try:
        # Load configuration
        config = load_config()
        cfg = extract_config_values(config)

        # Initialize hardware
        led_controller = LEDController(
            pin_num=cfg['pin_num'], 
            num_leds=cfg['num_leds'], 
            brightness=cfg['brightness']
        )
        animation_runner = AnimationRunner(led_controller)
        
        # Setup integrations
        integration_manager = setup_integrations(cfg, animation_runner)

        # Run startup animation
        animation_runner.run_startup_animation(
            cfg['startup_animation'], 
            brightness=cfg['brightness']
        )

        # Main loop
        while True:
            try:
                # Check if display should be on
                now_hour = time.localtime().tm_hour
                if (cfg['on_time'] != cfg['off_time'] and 
                    (cfg['brightness'] == 0 or not (cfg['on_time'] <= now_hour < cfg['off_time']))):
                    led_controller.turn_all_off()
                    time.sleep(cfg['poll_time'])
                    continue

                # Run integration cycle
                integration_manager.run_integration_cycle(
                    brightness=cfg['brightness'],
                    poll_time=cfg['poll_time'],
                    weather_display_time=4
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
