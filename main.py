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
        self.geometry(f"{screen_width - 380}x{screen_height - 280}")
        self.resizable(False, False)
        
        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
            except:
                pass

        self.configure(bg="#FFF3E0")
        self.force_topmost = False
        self.settings = load_settings()
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#FFF3E0")
        self.main_frame.pack(fill="both", expand=True)
        
        # Initialize attributes needed by timer
        self.countdown_label = None
        self.start_btn = None
        self.customize_btn = None
        self.timer = Timer(self, self.countdown_label, self.start_btn, self.customize_btn)
        
        # Load main screen
        load_main_screen(self)
        
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