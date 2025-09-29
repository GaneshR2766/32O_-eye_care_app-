import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from config.paths import ICON_FILE
from config.settings import load_settings, save_settings


def load_main_screen(app):
    """Modern, responsive home screen for 32O - Eye Care Reminder."""

    main_frame = app.main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # === Background Styling ===
    gradient_frame = ctk.CTkCanvas(main_frame, highlightthickness=0)
    gradient_frame.pack(fill="both", expand=True)
    gradient_frame.create_rectangle(
        0, 0, 2000, 2000,
        fill="#E8F1FA", outline=""
    )

    # === Fonts ===
    fonts = {
        "title": ctk.CTkFont("Segoe UI Semibold", 30),
        "subtitle": ctk.CTkFont("Segoe UI", 14),
        "timer": ctk.CTkFont("Poppins SemiBold", 48),
        "button": ctk.CTkFont("Poppins Medium", 18),
        "footer": ctk.CTkFont("Segoe UI", 12),
    }

    # === Main Card ===
    card = ctk.CTkFrame(
        main_frame,
        fg_color="white",
        corner_radius=20,
        border_width=0
    )
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)
    card.configure(width=420, height=580)

    # === Icon and Title ===
    try:
        img = Image.open(ICON_FILE).resize((110, 110))
        icon_img = ctk.CTkImage(img, size=(110, 110))
        ctk.CTkLabel(card, image=icon_img, text="").pack(pady=(15, 5))
    except Exception as e:
        print("Icon load error:", e)

    ctk.CTkLabel(
        card,
        text="32O – Eye Care Reminder",
        font=fonts["title"],
        text_color="#1D4E89"
    ).pack(pady=(0, 6))

    ctk.CTkLabel(
        card,
        text="Follow the 20–20–20 rule to relax your eyes",
        font=fonts["subtitle"],
        text_color="#6A7B89"
    ).pack()

    # === Timer Display ===
    countdown_label = ctk.CTkLabel(
        card,
        text="20:00",
        font=fonts["timer"],
        text_color="#004578",
        fg_color="#EFF4F9",
        corner_radius=16,
        width=200,
        height=75
    )
    countdown_label.pack(pady=(25, 20))

    # === Buttons Row ===
    button_frame = ctk.CTkFrame(card, fg_color="transparent")
    button_frame.pack(pady=(5, 20))

    start_btn = ctk.CTkButton(
        button_frame,
        text="Start Timer",
        font=fonts["button"],
        width=160,
        height=50,
        corner_radius=12,
        fg_color="#2E90E3",
        hover_color="#2469B3",
        command=app.timer.start_20min_timer
    )
    start_btn.pack(side="left", padx=12)

    reset_btn = ctk.CTkButton(
        button_frame,
        text="Reset",
        font=fonts["button"],
        width=160,
        height=50,
        corner_radius=12,
        fg_color="#E44E4E",
        hover_color="#B33A3A",
        command=app.timer.reset_timer
    )
    reset_btn.pack(side="left", padx=12)

    # === Customize Button ===
    customize_btn = ctk.CTkButton(
        card,
        text="⚙ Customize",
        font=("Poppins", 16),
        height=45,
        corner_radius=12,
        fg_color="#3A84C3",
        hover_color="#2C689A",
        command=lambda: open_customize_window(app)
    )
    customize_btn.pack(pady=(10, 15))

    # === Footer (with eye.png image) ===
    try:
        # Construct image path relative to current file (components folder)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        eye_icon_path = os.path.join(base_dir, "..", "assets", "eye.png")

        # Load image
        eye_img = Image.open(eye_icon_path).resize((18, 18))
        eye_icon = ImageTk.PhotoImage(eye_img)

        # Frame for footer
        footer_frame = ctk.CTkFrame(card, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=10)

        # Image + Text
        ctk.CTkLabel(
            footer_frame,
            image=eye_icon,
            text=""
        ).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            footer_frame,
            text="Designed by Ganesh R",
            font=fonts["footer"],
            text_color="#64748B"
        ).pack(side="left")

        # Prevent garbage collection
        footer_frame.image = eye_icon

    except Exception as e:
        print("Footer image load error:", e)
        ctk.CTkLabel(
            card,
            text="👁️ Designed by Ganesh R",
            font=fonts["footer"],
            text_color="#64748B"
        ).pack(side="bottom", pady=10)

    # === Link Controls ===
    app.countdown_label = countdown_label
    app.start_btn = start_btn
    app.customize_btn = customize_btn
    app.timer.countdown_label = countdown_label
    app.timer.start_btn = start_btn
    app.timer.customize_btn = customize_btn


# ----------------------------------------------------------------


def open_customize_window(app):
    """Modern settings UI with neumorphic panels."""
    main_frame = app.main_frame
    for w in main_frame.winfo_children():
        w.destroy()

    fonts = {
        "title": ctk.CTkFont("Segoe UI Semibold", 26),
        "section": ctk.CTkFont("Poppins SemiBold", 16),
        "text": ctk.CTkFont("Segoe UI", 14),
        "button": ctk.CTkFont("Poppins Medium", 16)
    }

    card = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=20)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.configure(width=460, height=600)
    card.pack_propagate(False)

    ctk.CTkLabel(
        card, text="⚙ Customize Settings", font=fonts["title"], text_color="#1D4E89"
    ).pack(pady=(15, 10))

    # Upload Section
    def upload_sound():
        file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if not file:
            return
        os.makedirs("sounds/user", exist_ok=True)
        dest = os.path.join("sounds/user", os.path.basename(file))
        with open(file, "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())
        if os.path.basename(file) not in app.settings["user_sounds"]:
            app.settings["user_sounds"].append(os.path.basename(file))
        save_settings(app.settings)
        refresh_sound_options()

    ctk.CTkButton(
        card,
        text="Upload New Alarm (.wav)",
        command=upload_sound,
        font=fonts["button"],
        fg_color="#4A90E2",
        hover_color="#3B72B2",
        corner_radius=10
    ).pack(pady=10)

    # Sound Options
    ctk.CTkLabel(card, text="Select Alarm Sound:", font=fonts["section"], text_color="#3A506B").pack(pady=(20, 5))
    sound_var = tk.StringVar(value=app.settings.get("selected_alarm", "default_alarm.wav"))
    sound_frame = ctk.CTkFrame(card, fg_color="#F4F6F8", corner_radius=10)
    sound_frame.pack(pady=5, padx=20, fill="x")

    def refresh_sound_options():
        for child in sound_frame.winfo_children():
            child.destroy()
        opts = ["default_alarm.wav"] + app.settings.get("user_sounds", [])
        for o in opts:
            ctk.CTkRadioButton(
                sound_frame,
                text=o,
                variable=sound_var,
                value=o,
                font=fonts["text"],
                fg_color="#1D4E89",
                hover_color="#163B66"
            ).pack(anchor="w", padx=20, pady=6)
    refresh_sound_options()

    # Nature Sound Toggle
    nature_var = tk.BooleanVar(value=app.settings.get("nature_sound", True))
    ctk.CTkCheckBox(
        card,
        text="Enable nature sound during break",
        variable=nature_var,
        font=fonts["text"],
        fg_color="#1D4E89",
        hover_color="#163B66"
    ).pack(pady=18)

    # Alarm Loop
    ctk.CTkLabel(card, text="Alarm Loop Style:", font=fonts["section"], text_color="#3A506B").pack(pady=(10, 5))
    loop_style = tk.IntVar(value=app.settings.get("alarm_loop_style", 1))
    option_box = ctk.CTkFrame(card, fg_color="#F4F6F8", corner_radius=10)
    option_box.pack(padx=20, fill="x")

    ctk.CTkRadioButton(
        option_box, text="Repeat every 5s", variable=loop_style, value=1, font=fonts["text"], fg_color="#1D4E89"
    ).pack(anchor="w", padx=20, pady=8)
    ctk.CTkRadioButton(
        option_box, text="Continuous Loop", variable=loop_style, value=2, font=fonts["text"], fg_color="#1D4E89"
    ).pack(anchor="w", padx=20, pady=8)

    # Save Button
    def save_and_back():
        app.settings.update({
            "selected_alarm": sound_var.get(),
            "nature_sound": nature_var.get(),
            "alarm_loop_style": loop_style.get()
        })
        save_settings(app.settings)
        load_main_screen(app)

    ctk.CTkButton(
        card,
        text="💾 Save & Back",
        command=save_and_back,
        font=fonts["button"],
        fg_color="#1D4E89",
        hover_color="#163B66",
        corner_radius=10,
        height=45
    ).pack(pady=(25, 10))
