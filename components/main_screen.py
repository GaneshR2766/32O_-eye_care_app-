import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk
from config.paths import ICON_FILE
from config.settings import load_settings, save_settings

def load_main_screen(app):
    main_frame = app.main_frame
    
    for widget in main_frame.winfo_children():
        widget.destroy()

    title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    title_frame.pack(pady=10)

    try:
        img = Image.open(ICON_FILE).resize((120, 120))
        icon_img = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
        icon_label = ctk.CTkLabel(title_frame, image=icon_img, text="")
        icon_label.image = icon_img
        icon_label.pack()
    except Exception as e:
        print(f"Error loading icon: {e}")

    label = ctk.CTkLabel(main_frame, text="32O - Eye Care Reminder", 
                         font=("Arial Rounded MT Bold", 28), text_color="#FF6F00")
    label.pack()

    ctk.CTkLabel(main_frame, text="Follow the 20-20-20 Rule to reduce eye strain",
                 font=("Arial", 14), text_color="#6D4C41").pack(pady=10)

    countdown_label = ctk.CTkLabel(main_frame, text="20:00", font=("Courier", 48, "bold"),
                                 text_color="#E65100", fg_color="white", corner_radius=12,
                                 width=180, height=70)
    countdown_label.pack(pady=10)

    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(pady=20)

    start_btn = ctk.CTkButton(btn_frame, text="Start", command=app.timer.start_20min_timer,
                             font=("Arial", 18), width=160, height=50, fg_color="#43A047", hover_color="#2E7D32")
    start_btn.pack(side="left", padx=10)

    reset_btn = ctk.CTkButton(btn_frame, text="Reset", command=app.timer.reset_timer,
                             font=("Arial", 18), width=160, height=50, fg_color="#F4511E", hover_color="#BF360C")
    reset_btn.pack(side="left", padx=10)

    customize_btn = ctk.CTkButton(main_frame, text="Customize", command=lambda: open_customize_window(app),
                                font=("Arial", 16), fg_color="#FFA726", hover_color="#FB8C00")
    customize_btn.pack(pady=15)

    ctk.CTkLabel(main_frame, text="Created by Ganesh R", font=("Arial", 12), text_color="#6D4C41").pack(side="bottom", pady=10)

    # Update timer with actual widget references
    app.countdown_label = countdown_label
    app.start_btn = start_btn
    app.customize_btn = customize_btn
    app.timer.countdown_label = countdown_label
    app.timer.start_btn = start_btn
    app.timer.customize_btn = customize_btn

def open_customize_window(app):
    main_frame = app.main_frame
    
    for widget in main_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(main_frame, text="Customize Settings", font=("Arial", 22, "bold"), text_color="#BF360C").pack(pady=10)

    def upload_sound():
        filepath = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if filepath:
            filename = os.path.basename(filepath)
            dest = os.path.join("sounds/user", filename)
            os.makedirs("sounds/user", exist_ok=True)
            try:
                with open(filepath, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                if filename not in app.settings["user_sounds"]:
                    app.settings["user_sounds"].append(filename)
                save_settings(app.settings)
                refresh_sound_options()
            except Exception as e:
                print(f"Error uploading sound: {e}")

    ctk.CTkButton(main_frame, text="Upload New Alarm (.wav)", command=upload_sound,
                  fg_color="#FFB74D", hover_color="#FFA726").pack(pady=10)

    sound_var = tk.StringVar(value=app.settings.get("selected_alarm", "default_alarm.wav"))

    def refresh_sound_options():
        for widget in sound_frame.winfo_children():
            widget.destroy()
        options = ["default_alarm.wav"] + app.settings.get("user_sounds", [])
        for name in options:
            ctk.CTkRadioButton(sound_frame, text=name, variable=sound_var, value=name, 
                              fg_color="#FF9800").pack(anchor="w", padx=10, pady=2)

    ctk.CTkLabel(main_frame, text="Select Alarm Sound:", font=("Arial", 16), text_color="#E65100").pack(pady=(15, 0))
    sound_frame = ctk.CTkFrame(main_frame, fg_color="#FFF3E0")
    sound_frame.pack(pady=5)

    refresh_sound_options()

    nature_var = tk.BooleanVar(value=app.settings.get("nature_sound", True))
    ctk.CTkCheckBox(main_frame, text="Enable nature sound during break", variable=nature_var,
                    fg_color="#FFB74D").pack(pady=15)

    loop_style = tk.IntVar(value=app.settings.get("alarm_loop_style", 1))
    ctk.CTkLabel(main_frame, text="Alarm Loop Style:", font=("Arial", 16), text_color="#E65100").pack()
    ctk.CTkRadioButton(main_frame, text="Option 1: Repeat every 5s", variable=loop_style, 
                       value=1, fg_color="#FF9800").pack(anchor="w", padx=30)
    ctk.CTkRadioButton(main_frame, text="Option 2: Continuous Loop", variable=loop_style, 
                       value=2, fg_color="#FF9800").pack(anchor="w", padx=30)

    ctk.CTkButton(main_frame, text="Save & Back", command=lambda: save_and_back(),
                  fg_color="#43A047", hover_color="#2E7D32").pack(pady=20)

    def save_and_back():
        app.settings.update({
            "selected_alarm": sound_var.get(),
            "nature_sound": nature_var.get(),
            "alarm_loop_style": loop_style.get()
        })
        save_settings(app.settings)
        load_main_screen(app)