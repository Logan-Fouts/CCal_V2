import os
import json
import logging
import tempfile
import shutil
import threading


class ConfigManager:
    """Manages configuration settings for the LED control system."""

    _lock = threading.Lock()

    def __init__(self, config_file: str):
        self._config_file = config_file
        self.conf = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from a JSON file."""
        if not os.path.isfile(self._config_file):
            raise FileNotFoundError(f"Config file '{self._config_file}' not found.")
        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    logging.error(f"Config file '{self._config_file}' is not valid JSON.")
                    raise ValueError("Config file is not a valid JSON object.")
                self.conf = config
        except json.JSONDecodeError as exc:
            logging.error(f"Failed to parse config file '{self._config_file}': {exc}")
            raise ValueError("Config file is not a valid JSON object.")
        except (OSError, ValueError) as exc:
            logging.error(f"Error loading config: {exc}")
            raise
        except Exception as exc:
            logging.exception(f"Unexpected error loading config: {exc}")
            raise ValueError("Failed to load config file.")

    def update_config(self, new_config: dict) -> bool:
        """Safely save the current configuration to the JSON file and reload it."""
        if not isinstance(new_config, dict):
            logging.error("Provided new_config is not a dictionary.")
            return False
        try:
            with self._lock:
                dir_name = os.path.dirname(self._config_file)
                with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding="utf-8") as tf:
                    json.dump(new_config, tf, indent=4)
                    tempname = tf.name
                shutil.move(tempname, self._config_file)
            self._load_config()
            return True
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            logging.error(f"Failed to save config file '{self._config_file}': {exc}")
            return False
        except Exception as exc:
            logging.exception(f"Unexpected error saving config file '{self._config_file}': {exc}")
            return False
