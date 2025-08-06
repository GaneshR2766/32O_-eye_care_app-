# break_screen.py (updated)
import customtkinter as ctk
import pygame
import time
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk
from config.paths import NATURE_FILES
from config.globals import nature_index
from utils.camera import is_user_peeking
from components.alarm import stop_alarm

def create_alarm_overlay(app):
    main_frame = app.main_frame
    
    for widget in main_frame.winfo_children():
        widget.destroy()
        
    main_frame.configure(fg_color="#FFE082")

    ctk.CTkLabel(
        main_frame, text="⏰ Eye Break Alert!",
        font=("Arial", 32, "bold"),
        text_color="#BF360C"
    ).pack(pady=50)

    ctk.CTkButton(
        main_frame, text="Continue (Space)",
        command=lambda: handle_continue_in_main(app),
        font=("Arial", 20),
        fg_color="#FF9800", hover_color="#FB8C00",
        corner_radius=12
    ).pack(pady=15)

    ctk.CTkButton(
        main_frame, text="Shutdown (Esc/Q)",
        command=lambda: handle_shutdown_in_main(app),
        font=("Arial", 20),
        fg_color="#FF5722", hover_color="#D84315",
        corner_radius=12
    ).pack(pady=10)

    app.bind("<Key>", lambda e: (
        handle_continue_in_main(app) if e.keysym == 'space' else
        handle_shutdown_in_main(app) if e.keysym.lower() in ('escape', 'q') else None
    ))

    app.force_topmost = True
    app.apply_topmost_behavior()

def handle_continue_in_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    stop_alarm()
    start_eye_break_main(app)

def handle_shutdown_in_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    stop_alarm()
    app.destroy()

def start_eye_break_main(app, reset=False):
    global nature_index
    main_frame = app.main_frame
    
    # Only destroy widgets if not a reset
    if not reset:
        for widget in main_frame.winfo_children():
            widget.destroy()

        main_frame.configure(fg_color="#FFF8E1")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=2)

        # Top frame for instructions and countdown
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0))

        ctk.CTkLabel(
            top_frame,
            text="\U0001f441\ufe0f  Look 20 ft away for 20 seconds",
            font=("Arial", 24),
            text_color="#FF6F00"
        ).pack(pady=(0, 20))

        counter_label = ctk.CTkLabel(
            top_frame,
            text="20",
            font=("DS-Digital", 64),
            text_color="#E65100"
        )
        counter_label.pack()

        # Bottom frame for camera feed
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))

        # Camera feed container
        camera_container = ctk.CTkFrame(bottom_frame, fg_color="#2B2B2B", corner_radius=10)
        camera_container.pack(pady=10, padx=20, fill="both", expand=True)

        # Camera label for displaying video feed
        camera_label = ctk.CTkLabel(camera_container, text="")
        camera_label.pack(pady=10, padx=10)

        # Status label for detection info
        status_label = ctk.CTkLabel(
            bottom_frame,
            text="Initializing camera...",
            font=("Arial", 14),
            text_color="#5D4037"
        )
        status_label.pack(pady=(10, 0))

        # Angle information label
        angle_label = ctk.CTkLabel(
            bottom_frame,
            text="Vertical: 0.0° | Horizontal: 0.0°",
            font=("Arial", 12),
            text_color="#5D4037"
        )
        angle_label.pack()

        # Store references for updates
        app.break_ui = {
            'counter_label': counter_label,
            'camera_label': camera_label,
            'status_label': status_label,
            'angle_label': angle_label,
            'nature_sound': None
        }
    else:
        # Reset the counter label for smooth transition
        app.break_ui['counter_label'].configure(text="20", text_color="#E65100")
        if app.break_ui['nature_sound']:
            app.break_ui['nature_sound'].stop()
            app.break_ui['nature_sound'] = None

    app.unbind("<Key>")
    app.force_topmost = True
    app.maintain_topmost()

    # Play nature sound (both for initial start and resets)
    if app.settings.get("nature_sound", True):
        try:
            current_nature_file = NATURE_FILES[nature_index % len(NATURE_FILES)]
            nature_index += 1
            nature_sound = pygame.mixer.Sound(str(current_nature_file))
            nature_sound.set_volume(1.0)
            nature_sound.play(-1)
            app.break_ui['nature_sound'] = nature_sound
        except Exception as e:
            print(f"Nature sound error: {e}")

    countdown_seconds = 20

    def update_camera_display(analysis):
        """Update the camera feed display with annotations"""
        if analysis is None:
            app.break_ui['camera_label'].configure(image=None)
            app.break_ui['status_label'].configure(text="Camera error")
            app.break_ui['angle_label'].configure(text="Vertical: -- | Horizontal: --")
            return

        frame = analysis['frame']
        
        # Add text annotations to the frame
        cv2.putText(frame, analysis['message'], (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Resize frame for display
        frame = cv2.resize(frame, (400, 300))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to CTkImage
        img = Image.fromarray(frame)
        ctk_img = ctk.CTkImage(light_image=img, size=(400, 300))
        
        app.break_ui['camera_label'].configure(image=ctk_img)
        
        # Update status labels
        app.break_ui['status_label'].configure(text=analysis['message'])
        if analysis['face_detected']:
            app.break_ui['angle_label'].configure(
                text=f"Vertical: {analysis['vert_angle']:.1f}° | Horizontal: {analysis['horiz_angle']:.1f}°"
            )

    def tick():
        nonlocal countdown_seconds

        if countdown_seconds == 0:
            if app.break_ui['nature_sound']:
                app.break_ui['nature_sound'].stop()
            show_post_break_main(app)
            return

        app.break_ui['counter_label'].configure(text=str(countdown_seconds), text_color="#E65100")
        app.apply_topmost_behavior()
        countdown_seconds -= 1

        def camera_check():
            try:
                peeking, analysis = is_user_peeking()
                app.after(0, lambda: update_camera_display(analysis))
                
                if peeking:
                    app.break_ui['counter_label'].configure(text="⛔ Eyes on screen!", text_color="red")
                    if app.break_ui['nature_sound']:
                        app.break_ui['nature_sound'].stop()
                    # Use reset=True for smooth transition
                    app.after(2000, lambda: start_eye_break_main(app, reset=True))
                else:
                    app.after(1000, tick)
            except Exception as e:
                print(f"[Camera Error] {e}")
                app.after(1000, tick)

        threading.Thread(target=camera_check, daemon=True).start()

    tick()

def show_post_break_main(app):
    main_frame = app.main_frame
    
    for widget in main_frame.winfo_children():
        widget.destroy()

    main_frame.configure(fg_color="#FFD180")

    ctk.CTkLabel(main_frame, text="Break Over", font=("Arial", 32), text_color="#BF360C").pack(pady=50)
    ctk.CTkButton(main_frame, text="Continue (Space)", command=lambda: restart_20min_main(app),
                  font=("Arial", 20), fg_color="#4CAF50", hover_color="#388E3C").pack(pady=15)
    ctk.CTkButton(main_frame, text="Shutdown (Esc/Q)", command=lambda: handle_shutdown_in_main(app),
                  font=("Arial", 20), fg_color="#F44336", hover_color="#D32F2F").pack(pady=10)

    app.bind("<Key>", lambda e: (
        restart_20min_main(app) if e.keysym == 'space' else
        handle_shutdown_in_main(app) if e.keysym.lower() in ('escape', 'q') else None
    ))

def restart_20min_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    app.unbind("<Key>")
    from components.main_screen import load_main_screen
    load_main_screen(app)
    app.timer.start_20min_timer()