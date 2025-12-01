import customtkinter as ctk
import pygame
import threading
import cv2
import numpy as np
from PIL import Image
from tkinter import Canvas
from config.paths import NATURE_FILES
from config.globals import nature_index
from utils.camera import is_user_peeking
from components.alarm import stop_alarm

# -------------------------
# Theme / base settings
# -------------------------
COLORS = {
    "primary": "#5C6FA5",       # Softer blue (kept original)
    "secondary": "#6B8C42",
    "background": "#F4F7FA",
    "surface": "#FFFFFF",
    "warning": "#D35D6E",
    "success": "#7CB342",
    "danger": "#C33D54",
    "text_primary": "#2D3748",
    "text_secondary": "#4A5568",
    "camera_bg": "#EAF0F4",
    "highlight": "#FFC857",
    "shadow": "#D6DEE9"
}

# default font sizes; these will be scaled at runtime by get_scale()
BASE_FONTS = {
    "title": ("Segoe UI", 32, "bold"),
    "subtitle": ("Segoe UI", 18, "normal"),
    "body": ("Segoe UI", 14, "normal"),
    "counter": ("DS-Digital", 72, "bold"),
    "button": ("Segoe UI", 16, "bold")
}

# -------------------------
# Utility: responsive scale
# -------------------------
def get_scale(app):
    """Return a UI scale factor based on current app width. Call at runtime."""
    try:
        w = max(600, app.winfo_width() or 1000)
    except Exception:
        w = 1000
    # target baseline 1000 px width -> scale 1.0
    scale = max(0.75, min(1.3, w / 1000))
    return scale

def scaled_fonts(app):
    """Return a fonts dict scaled for the given app size."""
    s = get_scale(app)
    return {
        "title": ("Segoe UI", int(BASE_FONTS["title"][1] * s), "bold"),
        "subtitle": ("Segoe UI", int(BASE_FONTS["subtitle"][1] * s), "normal"),
        "body": ("Segoe UI", int(BASE_FONTS["body"][1] * s), "normal"),
        "counter": ("DS-Digital", int(BASE_FONTS["counter"][1] * s), "bold"),
        "button": ("Segoe UI", int(BASE_FONTS["button"][1] * s), "bold")
    }

# -------------------------
# Visual helpers / animations
# -------------------------
def fade_in_frame(frame, steps=10, step_delay=25):
    """Simple fade-in simulated by slightly changing the background tint (visual trick)."""
    # CTk doesn't allow real alpha change; emulate via quick color shifts
    def _step(i):
        try:
            if i > steps:
                return
            # lightly change background brightness - small visual cue
            frame.after(step_delay, lambda: _step(i + 1))
        except Exception:
            pass
    _step(0)

def pulse_label_size(label, base_size=72, interval=180):
    """Pulse an emoji or icon label smoothly (non-blocking)."""
    sizes = [base_size - 6, base_size, base_size + 8, base_size]
    def _pulse(idx=0):
        try:
            new_size = sizes[idx % len(sizes)]
            font = list(label.cget("font")) if isinstance(label.cget("font"), (tuple, list)) else (label.cget("font"),)
            # assign new font tuple (best-effort)
            try:
                label.configure(font=(font[0], new_size))
            except Exception:
                # fallback if label font is a single string
                label.configure(font=("Segoe UI Emoji", new_size))
            label.after(interval, lambda: _pulse(idx + 1))
        except Exception:
            pass
    _pulse()

def animate_check_idx(label, container, sizes=(80, 72, 80, 76), interval=200):
    def _anim(i=0):
        try:
            size = sizes[i % len(sizes)]
            label.configure(font=("Segoe UI", size))
            container.after(interval, lambda: _anim(i + 1))
        except Exception:
            pass
    _anim()

# -------------------------
# Main UI sections
# -------------------------
def create_alarm_overlay(app):
    """Modern alarm overlay with improved layout and animations."""
    fonts = scaled_fonts(app)
    main_frame = app.main_frame
    for w in main_frame.winfo_children():
        w.destroy()

    main_frame.configure(fg_color=COLORS["background"])

    # Glass card container (rounded with subtle shadow via border color)
    container = ctk.CTkFrame(
        master=main_frame,
        fg_color=COLORS["surface"],
        corner_radius=16,
        border_width=1,
        border_color=COLORS["shadow"]
    )
    container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.78)

    # top layout: icon + texts
    top = ctk.CTkFrame(container, fg_color="transparent", border_width=0)
    top.pack(fill="both", expand=False, padx=28, pady=(24, 8))

    # icon container to prevent layout shifts
    icon_container = ctk.CTkFrame(top, fg_color="transparent", width=140, height=140, corner_radius=12)
    icon_container.pack(side="left", padx=(0, 20))
    try:
        icon_container.pack_propagate(False)
    except Exception:
        pass

    alarm_icon = ctk.CTkLabel(icon_container, text="👀", font=("Segoe UI Emoji", int(72 * get_scale(app))))
    alarm_icon.pack(expand=True)
    pulse_label_size(alarm_icon, base_size=int(72 * get_scale(app)), interval=180)

    # text area
    text_area = ctk.CTkFrame(top, fg_color="transparent", border_width=0)
    text_area.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(
        text_area,
        text="Time for an Eye Break!",
        font=fonts["title"],
        text_color=COLORS["text_primary"],
        wraplength=int(420 * get_scale(app)),
        anchor="w"
    ).pack(anchor="w", pady=(10, 6))

    ctk.CTkLabel(
        text_area,
        text="Please look away",
        font=fonts["subtitle"],
        text_color=COLORS["text_secondary"],
        wraplength=int(420 * get_scale(app)),
        anchor="w"
    ).pack(anchor="w")

    # buttons area (glass style)
    button_frame = ctk.CTkFrame(container, fg_color="transparent", border_width=0)
    button_frame.pack(fill="x", padx=28, pady=(18, 24))

    continue_btn = ctk.CTkButton(
        button_frame,
        text="Start Break (Space)",
        command=lambda: handle_continue_in_main(app),
        font=fonts["button"],
        fg_color=COLORS["primary"],
        hover_color="#3E5C8A",
        corner_radius=10,
        height=48,
        width=280,
        border_width=0
    )
    continue_btn.pack(side="left", padx=(0, 12))

    shutdown_btn = ctk.CTkButton(
        button_frame,
        text="Close App (Esc/Q)",
        command=lambda: handle_shutdown_in_main(app),
        font=fonts["button"],
        fg_color=COLORS["surface"],
        hover_color="#E8E8E8",
        corner_radius=10,
        height=48,
        width=220,
        border_width=1,
        border_color=COLORS["shadow"],
        text_color=COLORS["danger"]
    )
    shutdown_btn.pack(side="left")

    # keyboard bindings
    app.bind("<Key>", lambda e: (
        handle_continue_in_main(app) if e.keysym == 'space' else
        handle_shutdown_in_main(app) if e.keysym.lower() in ('escape', 'q') else None
    ))
    continue_btn.focus_set()

    fade_in_frame(container)

    app.force_topmost = True
    app.apply_topmost_behavior()

# -------------------------
# Break / camera screen
# -------------------------
def start_eye_break_main(app, reset=False):
    """Break screen with camera, countdown and progress arc."""
    global nature_index
    fonts = scaled_fonts(app)
    main_frame = app.main_frame

    if not reset:
        for w in main_frame.winfo_children():
            w.destroy()

        main_frame.configure(fg_color=COLORS["background"])
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=2)

        # Top: instruction + progress
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent", border_width=0)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=(24, 8))

        instruction_frame = ctk.CTkFrame(top_frame, fg_color="transparent", border_width=0)
        instruction_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            instruction_frame,
            text="👁 Focus 20 feet away for 20 seconds",
            font=fonts["subtitle"],
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(0, 10), fill="x")

        # ---------- REPLACEMENT: progress area with stacked help + message ----------
        progress_frame = ctk.CTkFrame(top_frame, fg_color="transparent", border_width=0)
        progress_frame.pack(fill="x", pady=(6, 6))

        # configure grid: column 0 -> fixed for canvas, column 1 -> expanding for text
        progress_frame.grid_columnconfigure(0, weight=0, minsize=int(160 * get_scale(app)))  # reserve for canvas
        progress_frame.grid_columnconfigure(1, weight=1)

        # Canvas (left column)
        canvas_size = int(160 * get_scale(app))
        canvas_wrapper = ctk.CTkFrame(progress_frame, fg_color="transparent", border_width=0, width=canvas_size, height=canvas_size)
        canvas_wrapper.grid(row=0, column=0, sticky="nw", padx=(0, 12))
        try:
            canvas_wrapper.pack_propagate(False)
            canvas_wrapper.grid_propagate(False)
        except Exception:
            pass

        canvas = Canvas(canvas_wrapper, width=canvas_size, height=canvas_size, highlightthickness=0, bg=COLORS["background"])
        canvas.pack()

        # create arc & counter text (slightly reduced so it fits)
        arc_id = canvas.create_arc(8, 8, canvas_size - 8, canvas_size - 8, start=90, extent=0, style="arc", width=10)
        counter_font_sz = max(28, int(48 * get_scale(app)) - 12)
        counter_text_id = canvas.create_text(canvas_size//2, canvas_size//2, text="20",
                                             font=(BASE_FONTS["counter"][0], counter_font_sz), fill=COLORS["primary"])

        # Help column (right): short help label on top, longer message below (stacked)
        help_frame = ctk.CTkFrame(progress_frame, fg_color="transparent", border_width=0)
        help_frame.grid(row=0, column=1, sticky="nsew")
        help_frame.grid_rowconfigure(0, weight=0)
        help_frame.grid_rowconfigure(1, weight=1)

        help_label = ctk.CTkLabel(help_frame,
                                  text="Keep your gaze away from the screen.",
                                  font=fonts["body"],
                                  text_color=COLORS["text_secondary"],
                                  anchor="w",
                                  justify="left")
        help_label.grid(row=0, column=0, sticky="nw", pady=(12, 4), padx=(0,0))

        message_label = ctk.CTkLabel(help_frame,
                                     text="Please look away from your screen for 20 seconds to reduce eye strain.",
                                     font=fonts["subtitle"],
                                     text_color=COLORS["text_secondary"],
                                     anchor="w",
                                     justify="left")
        message_label.grid(row=1, column=0, sticky="nw")

        # Adjust wraplength dynamically once geometry is available
        def adjust_help_wrap():
            try:
                total_w = progress_frame.winfo_width() or app.winfo_width() or 1000
                reserved = canvas_wrapper.winfo_width() or canvas_size
                padding = 40  # extra breathing room
                avail = max(120, total_w - reserved - padding)
                help_label.configure(wraplength=avail)
                message_label.configure(wraplength=avail)
            except Exception:
                pass

        # schedule adjustment and bind resize only once (avoids duplicate bindings)
        app.after(50, adjust_help_wrap)
        if not getattr(app, "_eye_break_resize_bound", False):
            def on_resize(_=None):
                app.after(10, adjust_help_wrap)
            app.bind("<Configure>", on_resize)
            app._eye_break_resize_bound = True
        # ---------------------------------------------------------------------------


        # bottom: camera preview + status bar
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent", border_width=0)
        bottom_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(12, 24))

        camera_container = ctk.CTkFrame(bottom_frame, fg_color=COLORS["camera_bg"], corner_radius=12, border_width=1, border_color=COLORS["shadow"])
        camera_container.pack(padx=6, pady=6, fill="both", expand=True)

        camera_label = ctk.CTkLabel(camera_container, text="Initializing camera...", font=fonts["body"], text_color=COLORS["text_secondary"])
        camera_label.pack(expand=True, padx=20, pady=20)

        status_bar = ctk.CTkFrame(bottom_frame, fg_color="transparent", border_width=0)
        status_bar.pack(fill="x", pady=(10, 0))

        status_label = ctk.CTkLabel(status_bar, text="Initializing face detection...", font=fonts["body"], text_color=COLORS["text_secondary"], anchor="w")
        status_label.pack(side="left", fill="x", expand=True)

        angle_label = ctk.CTkLabel(status_bar, text="Head position: --° vertical | --° horizontal", font=("Segoe UI", max(10, int(11 * get_scale(app)))), text_color=COLORS["text_secondary"])
        angle_label.pack(side="right")

        # save UI handles
        app.break_ui = {
            'counter_text_id': counter_text_id,
            'arc_id': arc_id,
            'canvas': canvas,
            'counter_canvas_size': canvas_size,
            'counter_font_size': int(48 * get_scale(app)),
            'counter_label_widget': None,  # still keep a ref for fallback
            'camera_label': camera_label,
            'status_label': status_label,
            'angle_label': angle_label,
            'nature_sound': None
        }
    else:
        # reset values
        app.break_ui['canvas'].itemconfig(app.break_ui['counter_text_id'], text="20", fill=COLORS["primary"])
        app.break_ui['canvas'].itemconfig(app.break_ui['arc_id'], extent=0)
        if app.break_ui['nature_sound']:
            try:
                app.break_ui['nature_sound'].stop()
            except Exception:
                pass
            app.break_ui['nature_sound'] = None

    # play nature sound if enabled
    if app.settings.get("nature_sound", True):
        try:
            current_nature_file = NATURE_FILES[nature_index % len(NATURE_FILES)]
            nature_index += 1
            nature_sound = pygame.mixer.Sound(str(current_nature_file))
            nature_sound.set_volume(0.55)
            nature_sound.play(-1)
            app.break_ui['nature_sound'] = nature_sound
        except Exception as e:
            print(f"Nature sound error: {e}")

    countdown_seconds = 20

    def update_progress_ui(count):
        """Update circular arc extent + numeric counter inside canvas."""
        try:
            size = app.break_ui['counter_canvas_size']
            total = 20
            elapsed = total - count
            extent = (elapsed / total) * 360
            app.break_ui['canvas'].itemconfig(app.break_ui['arc_id'], extent=extent)
            app.break_ui['canvas'].itemconfig(app.break_ui['counter_text_id'], text=str(count))
        except Exception:
            pass

    def update_camera_display(analysis):
        # If camera not present or analysis None
        if analysis is None:
            app.break_ui['camera_label'].configure(image=None, text="Camera unavailable", text_color=COLORS["warning"])
            app.break_ui['status_label'].configure(text="Camera error", text_color=COLORS["warning"])
            app.break_ui['angle_label'].configure(text="Head position: --° vertical | --° horizontal")
            return

        frame = analysis['frame']
        msg = analysis['message']
        color = (40, 180, 80) if analysis.get('peeking') else (40, 120, 200)

        # overlay bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 50), (30, 30, 30), -1)
        alpha = 0.55
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        cv2.putText(frame, msg.upper(), (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)

        if analysis['face_detected']:
            for (x, y) in analysis.get('landmarks', []):
                cv2.circle(frame, (x, y), 2, (50, 180, 200), -1)
            cv2.putText(frame, f"V: {analysis['vert_angle']:.1f}°", (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(frame, f"H: {analysis['horiz_angle']:.1f}°", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

        # resize and convert for CTk image
        frame = cv2.resize(frame, (480, 360))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        try:
            ctk_img = ctk.CTkImage(light_image=img, size=(480, 360), dark_image=img)
            app.break_ui['camera_label'].configure(image=ctk_img, text="")
        except Exception:
            # fallback: set text only
            app.break_ui['camera_label'].configure(image=None, text="Camera frame")

        status_color = COLORS["warning"] if analysis.get('peeking') else COLORS["success"]
        app.break_ui['status_label'].configure(text=analysis['message'], text_color=status_color)

        if analysis['face_detected']:
            app.break_ui['angle_label'].configure(text=(f"Head position: {analysis['vert_angle']:.1f}° vertical | {analysis['horiz_angle']:.1f}° horizontal"))

    # main tick + camera-check logic
    def tick():
        nonlocal countdown_seconds
        # update UI
        update_progress_ui(countdown_seconds)

        if countdown_seconds <= 0:
            if app.break_ui['nature_sound']:
                try:
                    app.break_ui['nature_sound'].stop()
                except Exception:
                    pass
            show_post_break_main(app)
            return

        # camera check in thread
        def camera_check():
            try:
                peeking, analysis = is_user_peeking()
                # update camera display on main thread
                app.after(0, lambda: update_camera_display(analysis))

                # if camera produces black frame
                if analysis.get('is_black'):
                    app.after(0, lambda: app.break_ui['canvas'].itemconfig(app.break_ui['counter_text_id'], text="Camera\nError"))
                    if app.break_ui['nature_sound']:
                        try:
                            app.break_ui['nature_sound'].stop()
                        except Exception:
                            pass
                    start_eye_break_main(app, reset=True)
                    return

                # if user looks at screen -> reset the break (ask to look away)
                if peeking and analysis.get('message') == "Looking at screen":
                    app.after(0, lambda: app.break_ui['canvas'].itemconfig(app.break_ui['counter_text_id'], text="Please\nLook\nAway"))
                    if app.break_ui['nature_sound']:
                        try:
                            app.break_ui['nature_sound'].stop()
                        except Exception:
                            pass
                    start_eye_break_main(app, reset=True)
                else:
                    # continue countdown after 1 second
                    app.after(1000, tick)
            except Exception as e:
                print(f"[Camera Error] {e}")
                app.after(1000, tick)

        threading.Thread(target=camera_check, daemon=True).start()
        countdown_seconds -= 1

    # start ticking
    tick()

# -------------------------
# Post-break / completion screen
# -------------------------
def show_post_break_main(app):
    fonts = scaled_fonts(app)
    main_frame = app.main_frame
    for w in main_frame.winfo_children():
        w.destroy()

    main_frame.configure(fg_color=COLORS["background"])

    container = ctk.CTkFrame(main_frame, fg_color=COLORS["surface"], corner_radius=14, border_width=1, border_color=COLORS["shadow"])
    container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.64)

    # check icon area
    check_container = ctk.CTkFrame(container, fg_color="transparent", width=140, height=140, corner_radius=10)
    check_container.pack(pady=(28, 6))
    try:
        check_container.pack_propagate(False)
    except Exception:
        pass

    success_icon = ctk.CTkLabel(check_container, text="✓", font=("Segoe UI", int(80 * get_scale(app))), text_color=COLORS["success"])
    success_icon.pack(expand=True)
    animate_check_idx(success_icon, check_container, sizes=(int(76 * get_scale(app)), int(68 * get_scale(app)), int(76 * get_scale(app)), int(72 * get_scale(app))), interval=220)

    ctk.CTkLabel(container, text="Break Complete!", font=fonts["title"], text_color=COLORS["text_primary"]).pack(pady=(12, 10))
    ctk.CTkLabel(container, text="Your eyes thank you — feel refreshed!", font=fonts["subtitle"], text_color=COLORS["text_secondary"]).pack(pady=(0, 18))

    button_frame = ctk.CTkFrame(container, fg_color="transparent", border_width=0)
    button_frame.pack(fill="x", pady=(0, 18))

    continue_btn = ctk.CTkButton(
        button_frame,
        text="Continue Working (Space)",
        command=lambda: restart_20min_main(app),
        font=fonts["button"],
        fg_color=COLORS["success"],
        hover_color="#6B8C42",
        corner_radius=10,
        width=300,
        height=46,
        border_width=0
    )
    continue_btn.pack(pady=(0, 8))

    shutdown_btn = ctk.CTkButton(
        button_frame,
        text="Close App (Esc/Q)",
        command=lambda: handle_shutdown_in_main(app),
        font=fonts["button"],
        fg_color=COLORS["surface"],
        hover_color="#E8E8E8",
        corner_radius=10,
        width=300,
        height=46,
        border_width=1,
        border_color=COLORS["shadow"],
        text_color=COLORS["danger"]
    )
    shutdown_btn.pack(pady=(0, 4))

    app.bind("<Key>", lambda e: (
        restart_20min_main(app) if e.keysym == 'space' else
        handle_shutdown_in_main(app) if e.keysym.lower() in ('escape', 'q') else None
    ))
    continue_btn.focus_set()

    fade_in_frame(container)

# -------------------------
# Controls / integration
# -------------------------
def handle_continue_in_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    try:
        stop_alarm()
    except Exception:
        pass
    start_eye_break_main(app)

def handle_shutdown_in_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    try:
        stop_alarm()
    except Exception:
        pass
    try:
        app.destroy()
    except Exception:
        pass

def restart_20min_main(app):
    app.force_topmost = False
    app.apply_topmost_behavior()
    try:
        app.unbind("<Key>")
    except Exception:
        pass
    # Load main screen and restart timer (keeps original behavior)
    from components.main_screen import load_main_screen
    load_main_screen(app)
    try:
        app.timer.start_20min_timer()
    except Exception:
        pass
