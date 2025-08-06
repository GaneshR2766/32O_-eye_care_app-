import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Path constants
SETTINGS_PATH = resource_path("settings.json")
DEFAULT_ALARM = resource_path("sounds/default_alarm.wav")
ICON_FILE = resource_path("assets/icon2.ico")
NATURE_FILES = [
    resource_path("nature/forest.wav"),
    resource_path("nature/rain.wav"), 
    resource_path("nature/waves.wav")
]