import customtkinter as ctk
import os
import sys
from engine.ghost_autopilot import init_ghost_engine, log_session_activity

class JarvisControlPanel(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- НАЛАШТУВАННЯ ВІКНА ---
        self.title("JARVIS | LOSTVAYNE-CORE")
        # Максимізую застосунок при запуску на LOSTVAYNE-LOQ
        self.after(0, lambda: self.state('zoomed'))
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Встановлюю іконку (має лежати в dashboard/icon.ico)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # --- ГРАФІЧНІ ЕЛЕМЕНТИ ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.label = ctk.CTkLabel(self.main_frame, text="LOSTVAYNE CONTROL CENTER",
                                  font=("Orbitron", 32, "bold"))
        self.label.pack(pady=40)

        # Кнопки керування
        self.create_button("ЗАПУСТИТИ GHOST MODE", self.run_ghost, "#2e7d32")
        self.create_button("СТАТУС БАЗИ ЗНАНЬ", self.check_db, "#d84315")
        self.create_button("ВІДКРИТИ ЗВІТ СЕСІЇ", self.open_report, "#455a64")
        self.create_button("JARVIS BRIDGE (ЕКСПОРТ)", self.export_bridge, "#1565c0")

        # Журнал
        self.textbox = ctk.CTkTextbox(self.main_frame, width=800, height=300, font=("Consolas", 14))
        self.textbox.pack(pady=30)
        self.log("Систему LOSTVAYNE-CORE розгорнуто на весь екран. Чекаю, Сер.")

    def create_button(self, text, command, color):
        btn = ctk.CTkButton(self.main_frame, text=text, command=command,
                             fg_color=color, font=("Arial", 16, "bold"), height=50, width=300)
        btn.pack(pady=10)

    def log(self, message):
        self.textbox.insert("end", f"\n[>] {message}")
        self.textbox.see("end")

    def open_report(self):
        report_path = os.path.join("engine", "data", "session_history.txt")
        if os.path.exists(report_path):
            os.startfile(report_path) # Відкриває блокнотом у Windows
            self.log("Звіт сесії відкрито.")
        else:
            self.log("Сер, звіт ще не створено.")

    def run_ghost(self):
        self.log("GHOST: Активація протоколів...")
        init_ghost_engine()

    def check_db(self):
        self.log("БАЗА: Сканую лекції ментора...")
        # Виклик вашої логіки search_brain

    def export_bridge(self):
        os.system("python export_context.py")
        self.log("BRIDGE: Зліпок надіслано на робочий стіл.")

if __name__ == "__main__":
    app = JarvisControlPanel()
    app.mainloop()