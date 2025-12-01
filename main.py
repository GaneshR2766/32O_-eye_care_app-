import customtkinter as ctk
import pygame
import os
import sys
from config.paths import ICON_FILE
from config.settings import load_settings
from components.main_screen import load_main_screen
from components.timer import Timer

class EyeCareApp(ctk.CTk):
    """
    Modified application that removes the native title bar (so there is no minimize/maximize)
    and provides a simple custom titlebar with only a Close button. This prevents minimizing
    via the window decorations. (Window manager shortcuts may still operate on some platforms;
    overrideredirect is the most reliable cross-platform way to remove minimize/maximize controls.)
    """
    def __init__(self):
        super().__init__()

        # Basic window sizing
        self.title("32O - Eye Protection")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width - 375}x{screen_height - 105}")
        # We still set resizable False but the native title bar is removed below.
        self.resizable(False, False)

        # Try to set icon (optional)
        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except Exception:
                pass

        # Apply overrideredirect to remove native title bar (no minimize/maximize/close)
        # We'll add a custom titlebar with only a Close button.
        try:
            self.overrideredirect(True)
        except Exception:
            # if overrideredirect isn't supported, fall back gracefully (native decorations remain)
            pass

        # Make sure ESC still closes the app for convenience
        self.bind("<Escape>", lambda e: self.destroy())

        # Enhanced eye-friendly colors & settings
        self.configure(bg="#F0F4F8")  # Soft blue-gray background
        self.force_topmost = False
        self.settings = load_settings()

        # Initialize pygame mixer (safe-guarded)
        try:
            pygame.mixer.init()
        except Exception:
            pass

        # Custom titlebar (simple, contains app title and close button)
        # keep it visually consistent with the app
        titlebar_height = 36
        try:
            titlebar = ctk.CTkFrame(self, height=titlebar_height, fg_color="#E8EDF3", corner_radius=0)
            titlebar.pack(side="top", fill="x")
            title_label = ctk.CTkLabel(titlebar, text="  32O - Eye Protection", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), anchor="w")
            title_label.pack(side="left", padx=(8,0))

            # Close button (only control provided)
            close_btn = ctk.CTkButton(titlebar, text="✕", width=36, height=26,
                                      command=lambda: self.destroy(),
                                      corner_radius=8, fg_color="#E05353", hover_color="#C83D3D")
            close_btn.pack(side="right", padx=8, pady=4)
        except Exception:
            # If CTk widgets fail here, ignore and continue; the app will still run.
            pass

        # Allow dragging the window by dragging the titlebar area
        def _start_move(event):
            try:
                self._drag_x = event.x
                self._drag_y = event.y
            except Exception:
                self._drag_x = 0
                self._drag_y = 0

        def _do_move(event):
            try:
                x = self.winfo_x() + (event.x - self._drag_x)
                y = self.winfo_y() + (event.y - self._drag_y)
                # ensure integer coordinates
                self.geometry(f"+{int(x)}+{int(y)}")
            except Exception:
                pass

        try:
            titlebar.bind("<Button-1>", _start_move)
            titlebar.bind("<B1-Motion>", _do_move)
            title_label.bind("<Button-1>", _start_move)
            title_label.bind("<B1-Motion>", _do_move)
        except Exception:
            pass

        # Create main frame with eye-protective colors (below the custom titlebar)
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#E8EDF3",  # Light blue-gray
            border_color="#D1DCE9",  # Soft border
            border_width=1,
            corner_radius=14  # Slightly smoother corners
        )
        # pack fill under the titlebar
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=(8,12))

        # Initialize attributes needed by timer
        self.countdown_label = None
        self.start_btn = None
        self.customize_btn = None
        # Timer expects the widget references (they will be set by load_main_screen)
        self.timer = Timer(self, self.countdown_label, self.start_btn, self.customize_btn)

        # Apply eye-friendly theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")  # Calmer blue-based theme

        # Set global font styles
        self.default_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")

        # Load main screen (this function should set countdown_label, start_btn, customize_btn)
        load_main_screen(self)

        # Apply consistent styling after short delay (allows widgets to be created)
        self.after(100, self._apply_eye_friendly_styles)

        # Optional: ensure the app is raised and focused (if force_topmost used elsewhere)
        if getattr(self, "force_topmost", False):
            try:
                self.lift()
                self.attributes("-topmost", True)
            except Exception:
                pass

    def _apply_eye_friendly_styles(self):
        """Apply optimized eye protection styles to all elements"""
        # Configure buttons with protective colors
        if self.start_btn:
            try:
                self.start_btn.configure(
                    fg_color="#2E90E3",        # Blue from rgb(46, 144, 227)
                    hover_color="#2B5C87",
                    text_color="#FFFFFF",
                    corner_radius=10,
                    border_width=0,
                    font=self.title_font
                )
            except Exception:
                pass

        if self.customize_btn:
            try:
                self.customize_btn.configure(
                    fg_color="#2E90E3",        # Matching blue
                    hover_color="#256FAF",
                    text_color="#FFFFFF",
                    corner_radius=10,
                    border_width=0,
                    font=self.default_font
                )
            except Exception:
                pass

        # Configure timer display
        if self.countdown_label:
            try:
                self.countdown_label.configure(
                    text_color="#3A506B",      # Soft navy blue
                    font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold")
                )
            except Exception:
                pass

        # Apply consistent styling to CTk children inside main_frame
        try:
            for widget in self.main_frame.winfo_children():
                try:
                    if isinstance(widget, ctk.CTkBaseClass):
                        widget.configure(font=self.default_font)
                except Exception:
                    pass
        except Exception:
            pass

    def apply_topmost_behavior(self):
        if self.force_topmost:
            try:
                self.lift()
                self.attributes("-topmost", True)
                self.focus_force()
            except Exception:
                pass
        else:
            try:
                self.attributes("-topmost", False)
            except Exception:
                pass

    def maintain_topmost(self):
        if self.force_topmost:
            try:
                self.lift()
                self.attributes("-topmost", True)
                self.after(500, self.maintain_topmost)
            except Exception:
                pass

if __name__ == "__main__":
    app = EyeCareApp()
    app.mainloop()
