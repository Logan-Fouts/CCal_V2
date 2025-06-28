import json

class CONFIG_MANAGER:
    def __init__(self):
        self.CONFIG_FILE = "/home/ccaluser/CCal_V2/config.json"

    def load_config(self):
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config
        except:
            print("No config found. Using defaults (if any).")
            return {}

    def save_config(self, config):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f)
        print("Config saved.")

    def unquote(self, string):
        """Basic URL decoding"""
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

