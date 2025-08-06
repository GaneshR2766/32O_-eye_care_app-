import time
import pygame
import os
import threading
from config.paths import resource_path, DEFAULT_ALARM, NATURE_FILES
from config.settings import load_settings
from config.globals import nature_index, alarm_active, alarm_start_time

def play_alarm_loop(app):
    global alarm_active, alarm_start_time
    alarm_active = True
    alarm_start_time = time.time()
    settings = load_settings()

    def loop():
        global nature_index
        selected = settings["selected_alarm"]
        if selected in settings.get("user_sounds", []):
            path = resource_path(os.path.join("sounds", "user", selected))
        else:
            path = resource_path(os.path.join("sounds", selected))

        if not os.path.exists(path):
            print("Alarm file missing. Reverting to default.")
            path = DEFAULT_ALARM

        if settings.get("alarm_loop_style", 1) == 2:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)

        while alarm_active:
            if settings.get("alarm_loop_style", 1) == 1:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                time.sleep(5)
            if time.time() - alarm_start_time > 60:
                break
        pygame.mixer.music.stop()
        app.after(0, lambda: show_continue_shutdown_buttons(app))

    threading.Thread(target=loop, daemon=True).start()

def stop_alarm():
    global alarm_active
    alarm_active = False
    pygame.mixer.music.stop()

def show_alarm_overlay(app):
    from components.break_screen import create_alarm_overlay
    create_alarm_overlay(app)
    play_alarm_loop(app)

def show_continue_shutdown_buttons(app):
    pass