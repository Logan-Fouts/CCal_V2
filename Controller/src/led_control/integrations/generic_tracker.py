"""
Default tracker users can use to track anything.

Features:
- Define new tracker instance from a file
- Includes array of previus 28 days of data a frequency array
- Defines color for activity tracker
- Users define this tracker themselves in the web gui
- Web gui writes the config file for this tracker including adding new activity data
"""

import time
import sys

from led_control.core.config_manager import ConfigManager

class GenericTracker:
    """
    Default tracker users can use to track anything.
    The only way this should update the data array is the new day shifting.
    """

    def __init__(self, configPath):
        """
        All this takes is a path to a config file.
        The config file should be a JSON file with the following structure:
        {
            "name": "My Generic Tracker",
            "data": [0, 1, 0, 2, ..., 0],  # 28 days of data
            "event": [R, G, B],
            "no_events": [R, G, B]
        }
        """
        # self.currDay = time.localtime().tm_mday
        # Temporarily set day to previous day to force shift on first get_data call
        self.currDay = (time.localtime().tm_mday - 1) % 31

        self.configPath = configPath
        self._get_config()


    def _get_config(self):
        try:
            self.config_manager = ConfigManager(self.configPath)
            config = self.config_manager.conf
        except Exception as exc:
            print(f"[ERROR] Failed to load config: {exc}")
            sys.exit(1)

        self.name = config.get("name", "Generic Tracker")
        self.data = config.get("data", [0] * 28)
        self.metric = config.get("metric", "units")

        event_color = config.get("event", [0, 255, 0])
        no_event_color = config.get("no_events", [0, 0, 0])
        self.color = {"event": event_color, "no_events": no_event_color}


    def _save_config(self):
        """
        Save the current configuration to the config file.
        """
        new_config = {
            "name": self.name,
            "data": self.data,
            "event": self.color["event"],
            "no_events": self.color["no_events"],
            "metric": self.metric
        }
        try:
            self.config_manager = ConfigManager(self.configPath)
            self.config_manager.update_config(new_config)
        except Exception as exc:
            print(f"[ERROR] Failed to save config: {exc}")

    def _is_new_day(self):
        """
        Check if a new day has started.
        """
        newDay = time.localtime().tm_mday
        if newDay != self.currDay:
            self.currDay = newDay
            return True
        return False
    
    def _shift_data(self):
        """
        Shift the data array to account for a new day.
        """
        self.data = [0] + self.data[:-1]
        self._save_config()

    def get_data(self):
        """
        Get the frequency array of activity data.
        28 days of data, with the most recent day at index 0.
        When a new day is detected, shift the array and add a new day with 0 activity.
        """
        self._get_config()
        if self._is_new_day(): self._shift_data()
        return self.data

    def get_color(self):
        """
        Get the color mapping for events and no events.
        """
        return self.color

    def get_name(self):
        """
        Get the name of the tracker.
        """
        return self.name

