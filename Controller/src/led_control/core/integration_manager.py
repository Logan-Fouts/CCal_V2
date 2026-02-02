"""
Integration manager for handling all external service integrations.

Centralizes the logic for fetching and displaying data from GitHub, Strava,
Weather, and other integrations. Uses OOP so each integration is encapsulated
in its own class with a common interface.
"""

import time


class IntegrationManager:
    """Manages all external service integrations and their display logic."""
    
    def __init__(self, animation_runner, trackers=[], weather_tracker=[]):
        self.animation_runner = animation_runner
        self.trackers = trackers
        self.weather_tracker = weather_tracker
        self.iterations_per_cycle = 2
        
    def update_calendar_display(self, brightness=0.8, poll_time=90):
        """
        Update the calendar display with activity data.
        """
        sleepDuration = (poll_time / (len(self.trackers))) / self.iterations_per_cycle

        for _ in range(self.iterations_per_cycle):
            for tracker in self.trackers:
                try:
                    activity = tracker.get_activity()
                    if sum(activity) > 0:
                        self.animation_runner.update_calendar(
                            activity, brightness=brightness, colors=tracker.get_colors()
                        )
                    time.sleep(sleepDuration)
                except Exception as exc:
                    print(f"[ERROR] Failed to fetch data from {tracker.__class__.__name__}: {exc}")                

        return True
    
    def handle_weather_animation(self, brightness=0.8):
        """Handle weather animation display."""
        if not self.weather_tracker:
            return False
            
        try:
            weather = self.weather_tracker.get_weather()
            if weather is not None:
                self.animation_runner.run_weather_animation(
                    weather, brightness=brightness
                )
                return True
        except Exception as exc:
            print(f"[ERROR] Failed to fetch weather: {exc}")
        
        return False
    
    def run_integration_cycle(self, brightness=0.8, poll_time=90, weather_display_time=4):
        """
        Run a complete cycle of all integrations.
        """
        
        self.update_calendar_display(brightness=brightness, poll_time=poll_time)
        self.handle_weather_animation(brightness=brightness)
        time.sleep(weather_display_time)

