import threading

class Timer:
    def __init__(self, app, countdown_label, start_btn, customize_btn):
        self.app = app
        self.countdown_label = countdown_label
        self.start_btn = start_btn
        self.customize_btn = customize_btn
        self.timer_running = False
        self.total_seconds = 0
        self.timer_thread = None

    def start_20min_timer(self):
        self.start_btn.configure(state="disabled")
        self.customize_btn.configure(state="disabled")
        self.total_seconds = 5  # 20 minutes in seconds
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.timer_countdown, daemon=True)
        self.timer_thread.start()

    def reset_timer(self):
        self.timer_running = False
        self.total_seconds = 20 * 60
        self.countdown_label.configure(text="20:00")
        self.start_btn.configure(state="normal")
        self.customize_btn.configure(state="normal")

    def timer_countdown(self):
        def update():
            if not self.timer_running:
                return
                
            mins, secs = divmod(self.total_seconds, 60)
            self.countdown_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.app.apply_topmost_behavior()

            if self.total_seconds > 0:
                self.total_seconds -= 1
                self.app.after(1000, update)
            else:
                self.timer_running = False
                from components.alarm import show_alarm_overlay
                show_alarm_overlay(self.app)

        self.app.after(0, update)