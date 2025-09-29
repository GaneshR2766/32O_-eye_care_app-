import PyInstaller.__main__
import os
import shutil

# Configuration
APP_NAME = "EyeCareReminder"
MAIN_SCRIPT = "app.py"  # Replace with your main entry file
ICON_PATH = "assets/app_icon.ico"  # Replace with your icon path
ADD_DATA = [
    ("sounds/", "sounds"),
    ("assets/", "assets"),
    ("haarcascades/", "haarcascades")  # For OpenCV face detection
]
ADD_BINARY = []

# PyInstaller command setup
params = [
    MAIN_SCRIPT,
    "--name", APP_NAME,
    "--onefile",
    "--windowed",
    "--icon", ICON_PATH,
    "--add-data", f"{os.pathsep.join(ADD_DATA)}",
    "--hidden-import", "pygame._sdl2.audio",  # Required for pygame audio
    "--hidden-import", "customtkinter",
    "--hidden-import", "PIL",
    "--collect-data", "customtkinter",
    "--collect-data", "pygame",
    "--paths", os.path.dirname(os.path.abspath(__file__))
]

# Add binaries if needed (like OpenCV DLLs)
for binary in ADD_BINARY:
    params.extend(["--add-binary", binary])

# Build the executable
print("Building executable...")
PyInstaller.__main__.run(params)

print("\nBuild complete! Executable is in the 'dist' folder")