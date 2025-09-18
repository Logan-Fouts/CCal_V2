"""Configuration manager for CCal_V2."""

import json
import os
import traceback


class ConfigManager:
    """Handles loading and saving configuration.""" 

    def __init__(self, config_file="/home/ccal/CCal_V2/config.json"):
        """Initialize ConfigManager with a config file path."""
        self.config_file = config_file

    def load_config(self):
        """Load configuration from file."""
        if not os.path.isfile(self.config_file):
            print(
                f"[WARN] Config file '{self.config_file}' not found. Using defaults (if any)."
            )
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    print(
                        f"[ERROR] Config file '{self.config_file}' is not a valid JSON object."
                    )
                    return {}
                return config
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Failed to parse config file '{self.config_file}': {exc}")
            return {}
        except Exception as exc:
            print(f"[ERROR] Unexpected error loading config: {exc}")
            traceback.print_exc()
            return {}

    def save_config(self, config):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            print("Config saved.")
        except Exception as exc:
            print(f"[ERROR] Failed to save config: {exc}")
            traceback.print_exc()

    def unquote(self, string):
        """Basic URL decoding."""
        if not isinstance(string, str):
            print("[WARN] unquote() received non-string input.")
            return string
        replacements = {"%20": " ", "%40": "@", "%21": "!", "%24": "$", "%26": "&"}
        for code, char in replacements.items():
            string = string.replace(code, char)
        return string
