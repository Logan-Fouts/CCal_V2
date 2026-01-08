"""
Integration manager for handling all external service integrations.

Centralizes the logic for fetching and displaying data from GitHub, Strava,
Weather, and Spotify integrations.
"""

import time


class IntegrationManager:
    """Manages all external service integrations and their display logic."""
    
    def __init__(self, animation_runner, github_tracker=None, strava_tracker=None, 
                 weather_tracker=None, spotify_tracker=None):
        self.animation_runner = animation_runner
        self.github_tracker = github_tracker
        self.strava_tracker = strava_tracker
        self.weather_tracker = weather_tracker
        self.spotify_tracker = spotify_tracker
        
        self.github_colors = {
            "no_events": [30, 30, 30],
            "event": [0, 255, 0]
        }
        
        self.strava_colors = {
            "no_events": [30, 30, 30], 
            "event": [255, 100, 0]
        }
    
    def update_calendar_display(self, brightness=0.8, colors=None, poll_time=90):
        """
        Update the calendar display with activity data.
        """
        if colors is None:
            colors = self.github_colors
            
        if self.github_tracker:
            try:
                event_counts = self.github_tracker.get_event_counts()
                self.animation_runner.update_calendar(
                    event_counts, brightness=brightness, colors=colors
                )
            except Exception as exc:
                print(f"[ERROR] Failed to fetch GitHub events: {exc}")

        time.sleep(poll_time / 2) 

        if self.strava_tracker:
            try:
                if self.strava_tracker.is_authenticated():
                    activity_counts = self.strava_tracker.get_activity_counts()
                    if sum(activity_counts) > 0:
                        self.animation_runner.update_calendar(
                            activity_counts, brightness=brightness, colors=self.strava_colors
                        )
            except Exception as exc:
                print(f"[ERROR] Failed to fetch Strava activities: {exc}")
        
        return True
    
    def handle_weather_animation(self, brightness=0.8):
        """Handle weather animation display."""
        if not self.weather_tracker:
            return False
            
        try:
            weather = self.weather_tracker.get_current_weather()
            if weather is not None:
                self.animation_runner.run_weather_animation(
                    weather, brightness=brightness
                )
                return True
        except Exception as exc:
            print(f"[ERROR] Failed to fetch weather: {exc}")
        
        return False
    
    def handle_spotify_animation(self, duration=5, brightness=0.8):
        """Handle Spotify music animation if playing."""
        if not self.spotify_tracker:
            return False
            
        try:
            is_playing = self.spotify_tracker.is_playing()
            if is_playing:
                end_time = time.time() + duration
                self.animation_runner.spotify_music_animation_loop(
                    end_time, brightness=brightness
                )
                return True
        except Exception as exc:
            print(f"[ERROR] Failed to check Spotify playback: {exc}")
        
        return False
    
    def run_integration_cycle(self, brightness=0.8, poll_time=10, weather_display_time=4):
        """
        Run a complete cycle of all integrations.
        """
        
        self.update_calendar_display(brightness=brightness, poll_time=poll_time)
        time.sleep(poll_time / 2)
        
        self.handle_weather_animation(brightness=brightness)
        time.sleep(weather_display_time)

        self.handle_spotify_animation(brightness=brightness)