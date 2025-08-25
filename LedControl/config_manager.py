import json
import os
import sys
import traceback

class CONFIG_MANAGER:
    def __init__(self, config_file="/home/ccalv2/CCal_V2/config.json"):
        self.CONFIG_FILE = config_file

    def load_config(self):
        if not os.path.isfile(self.CONFIG_FILE):
            print(f"[WARN] Config file '{self.CONFIG_FILE}' not found. Using defaults (if any).")
            return {}
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    print(f"[ERROR] Config file '{self.CONFIG_FILE}' is not a valid JSON object.")
                    return {}
                return config
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse config file '{self.CONFIG_FILE}': {e}")
            return {}
        except Exception as e:
            print(f"[ERROR] Unexpected error loading config: {e}")
            traceback.print_exc()
            return {}

    def save_config(self, config):
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            print("Config saved.")
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            traceback.print_exc()

    def unquote(self, string):
        """Basic URL decoding"""
        if not isinstance(string, str):
            print("[WARN] unquote() received non-string input.")
            return string
        replacements = {
            '%20': ' ',
            '%40': '@',
            '%21': '!',
            '%24': '$',
            '%26': '&'
        }
        for code, char in replacements.items():
            string = string.replace(code, char)
        return string

