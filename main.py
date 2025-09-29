import customtkinter as ctk
import pygame
import os
import sys
from config.paths import ICON_FILE
from config.settings import load_settings
from components.main_screen import load_main_screen
from components.timer import Timer

class EyeCareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("32O - Eye Protection")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width - 700}x{screen_height - 135}")
        self.resizable(False, False)
        
        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except:
                pass

        # Enhanced eye-friendly colors
        self.configure(bg="#F0F4F8")  # Soft blue-gray background
        self.force_topmost = False
        self.settings = load_settings()
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create main frame with eye-protective colors
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#E8EDF3",  # Light blue-gray
            border_color="#D1DCE9",  # Soft border
            border_width=1,
            corner_radius=14  # Slightly smoother corners
        )
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Initialize attributes needed by timer
        self.countdown_label = None
        self.start_btn = None
        self.customize_btn = None
        self.timer = Timer(self, self.countdown_label, self.start_btn, self.customize_btn)
        
        # Apply eye-friendly theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")  # Calmer blue-based theme
        
        # Set global font styles
        self.default_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        
        # Load main screen
        load_main_screen(self)

        # Apply consistent styling
        self.after(100, self._apply_eye_friendly_styles)
        
    def _apply_eye_friendly_styles(self):
        """Apply optimized eye protection styles to all elements"""
        # Configure buttons with protective colors
        if self.start_btn:
            self.start_btn.configure(
                fg_color="#2E90E3",        # Blue from rgb(46, 144, 227)
                hover_color="#2B5C87", 
                text_color="#FFFFFF",
                corner_radius=10,
                border_width=0,
                font=self.title_font
            )
        if self.customize_btn:
            self.customize_btn.configure(
                fg_color="#2E90E3",        # Matching blue
                hover_color="#256FAF",  
                text_color="#FFFFFF",
                corner_radius=10,
                border_width=0,
                font=self.default_font
            )
        
        # Configure timer display
        if self.countdown_label:
            self.countdown_label.configure(
                text_color="#3A506B",      # Soft navy blue
                font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold")
            )
            
        # Apply consistent styling to all widgets
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkBaseClass):
                try:
                    widget.configure(font=self.default_font)
                except:
                    pass
                
    def apply_topmost_behavior(self):
        if self.force_topmost:
            self.lift()
            self.attributes("-topmost", True)
            self.focus_force()
        else:
            self.attributes("-topmost", False)
            
    def maintain_topmost(self):
        if self.force_topmost:
            self.lift()
            self.attributes("-topmost", True)
            self.after(500, self.maintain_topmost)

if __name__ == "__main__":
    app = EyeCareApp()
    app.mainloop()