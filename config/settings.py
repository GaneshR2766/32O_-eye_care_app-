import json
import os
from config.paths import SETTINGS_PATH

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        default_settings = {
            "selected_alarm": "default_alarm.wav",
            "user_sounds": [],
            "nature_sound": True,
            "alarm_loop_style": 1
        }
        with open(SETTINGS_PATH, "w") as f:
            json.dump(default_settings, f)
        return default_settings
    
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)