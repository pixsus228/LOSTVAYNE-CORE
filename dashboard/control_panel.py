import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import psutil
import random
import time
from datetime import datetime

# --- Налаштування СТИЛЮ LOSTVAYNE-CORE (Stark Pro) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class LostvayneControlPanel(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Налаштування вікна та фону
        self.title("LOSTVAYNE SYSTEM CORE - КОНТРОЛЬНА ПАНЕЛЬ v2.4")
        self.geometry("1100x700")
        self.configure(fg_color="#0D0D0D")  # Ультра-чорний фон (як на фото)

        # Створення сітки
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- ЛІВА ПАНЕЛЬ (Віджети та Монітор заліза) ---
        # Використовуємо межі, щоб створити ефект складного модуля (border_width=2, border_color="#1F1F1F")
        self.left_panel = ctk.CTkFrame(self, fg_color="#101010", corner_radius=0, border_width=2,
                                       border_color="#1F1F1F")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Логотип (Червоний пульсуючий щит з фото_10.png)
        self.logo_label = ctk.CTkLabel(self.left_panel, text="🛡️", font=("Arial", 60),
                                       text_color="#FF0000")  # Червоний неон
        self.logo_label.pack(pady=(20, 5))
        self.title_label = ctk.CTkLabel(self.left_panel, text="ЯДРО LOSTVAYNE CORE", font=("Verdana", 16, "bold"),
                                        text_color="#A0A0A0")
        self.title_label.pack(pady=(0, 10))
        self.status_core = ctk.CTkLabel(self.left_panel, text="🟢 ЗАХИСТ: АКТИВНИЙ", font=("Robot", 12),
                                        text_color="#28A745")  # Зелений
        self.status_core.pack()

        # Розділ заліза (Real-time Telemetry)
        self.hardware_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.hardware_frame.pack(pady=20, fill="x", padx=10)

        # Створення модулів для заліза
        def create_hardware_bar(parent, label_text, value_text, color):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(pady=5, fill="x")
            lbl = ctk.CTkLabel(frame, text=label_text, font=("Robot", 11), text_color="#A0A0A0", anchor="w")
            lbl.pack(side="left")
            val = ctk.CTkLabel(frame, text=value_text, font=("Verdana", 11, "bold"), text_color=color, anchor="e")
            val.pack(side="right")
            progress = ctk.CTkProgressBar(parent, orientation="horizontal", height=6, progress_color=color,
                                          fg_color="#303030")
            progress.set(0.6)  # Приклад значення
            progress.pack(pady=(0, 10), fill="x")
            return val, progress

        self.cpu_val, self.cpu_bar = create_hardware_bar(self.hardware_frame, "НАВАНТАЖЕННЯ CPU:", "58%",
                                                         "#FFC107")  # Янтарний
        self.ram_val, self.ram_bar = create_hardware_bar(self.hardware_frame, "ВИКОРИСТАННЯ RAM:", "3.1 ГБ",
                                                         "#007BFF")  # Синій
        self.temp_val, self.temp_bar = create_hardware_bar(self.hardware_frame, "ТЕМПЕРАТУРА LOQ:", "45°C",
                                                           "#17A2B8")  # Тіловий

        # --- ПРАВА ПАНЕЛЬ (Динамічні графіки, Вивід тексту, Кнопки) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(0, weight=1)  # Графік
        self.right_panel.grid_rowconfigure(1, weight=2)  # Вивід тексту
        self.right_panel.grid_rowconfigure(2, weight=1)  # Кнопки

        # 1. Секція графіка (Real-time CPU Wave)
        self.graph_frame = ctk.CTkFrame(self.right_panel, fg_color="#101010", border_width=1, border_color="#1F1F1F")
        self.graph_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.graph_label = ctk.CTkLabel(self.graph_frame, text="ПОТОКИ CPU (РЕАЛЬНИЙ ЧАС)", font=("Robot", 13),
                                        text_color="#A0A0A0")
        self.graph_label.pack(pady=5, anchor="w", padx=10)

        # Складний графік на базі Tkinter Canvas (для візуальних ефектів)
        self.canvas = tk.Canvas(self.graph_frame, width=600, height=120, bg="#0A0A0A", highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)
        self.canvas.create_line(0, 60, 600, 60, fill="#202020", width=1, dash=(5, 5))  # Розмітка

        # 2. Поле виводу тексту відповіді JARVIS (Янтарний фокус з фото)
        self.output_frame = ctk.CTkFrame(self.right_panel, fg_color="#121212", border_width=1, border_color="#FFC107",
                                         corner_radius=5)  # Золота межа
        self.output_frame.grid(row=1, column=0, sticky="nsew", pady=10)

        self.output_title = ctk.CTkLabel(self.output_frame, text="💬 ВІДПОВІДЬ JARVIS:", font=("Robot", 12, "bold"),
                                         text_color="#FFC107")
        self.output_title.pack(pady=5, anchor="w", padx=15)

        self.response_text = ctk.CTkTextbox(self.output_frame, fg_color="transparent", font=("Consolas", 14),
                                            text_color="#E0E0E0", wrap="word")
        self.response_text.pack(expand=True, fill="both", padx=15, pady=(0, 15))
        self.response_text.insert("0.0",
                                  "Очікую команду, Сер... LOSTVAYNE CORE активовано.\nНа годиннику 23:36. Система готова до роботи.")

        # 3. Кнопки Керування (Neon Focus)
        self.buttons_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, sticky="nsew", pady=10)

        # Створення неонових кнопок з рамками та іконками
        def create_neon_button(parent, text, icon, color):
            btn = ctk.CTkButton(parent, text=text, font=("Verdana", 13, "bold"), height=45, corner_radius=5,
                                border_width=2, border_color=color, fg_color="transparent", text_color=color)
            btn.pack(side="left", expand=True, padx=5)

            # Ефект наведення
            def on_enter(e): btn.configure(fg_color=color, text_color="#0D0D0D")

            def on_leave(e): btn.configure(fg_color="transparent", text_color=color)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn

        self.btn_ai = create_neon_button(self.buttons_frame, "ЗАПУСТИТИ ШІ", "🔴", "#FF4136")  # Червоний неон
        self.btn_db = create_neon_button(self.buttons_frame, "КЕРУВАТИ БД", "🛠️", "#007BFF")  # Синій неон
        self.btn_logs = create_neon_button(self.buttons_frame, "ЛОГИ", "📝", "#6F42C1")  # Фіолетовий неон
        self.btn_backup = create_neon_button(self.buttons_frame, "КОПІЯ", "💾", "#E83E8C")  # Рожевий неон

        # --- НИЖНІЙ СТАТУС БАР (Кібер-блакитний неон з фото) ---
        self.status_bar = ctk.CTkFrame(self, fg_color="#101010", height=30, corner_radius=0, border_width=1,
                                       border_color="#1F1F1F")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.lbl_status_left = ctk.CTkLabel(self.status_bar,
                                            text="КОНТЕКСТ ШІ: 4.2MB | ЗАХИСТ: АКТИВНИЙ | Lostvayne Core v2.4",
                                            font=("Robot", 11), text_color="#00FFFF")  # Ціан
        self.lbl_status_left.pack(side="left", padx=15)

        self.lbl_time = ctk.CTkLabel(self.status_bar, text="", font=("Robot", 11), text_color="#00FFFF")
        self.lbl_time.pack(side="right", padx=15)
        self.update_time_realtime()

    # --- ЛОГІКА ТА ДИНАМІКА ---
    def update_time_realtime(self):
        current_time = datetime.now().strftime("%H:%M:%S | %d.%m.%Y")
        self.lbl_time.configure(text=current_time)
        self.after(1000, self.update_time_realtime)


if __name__ == "__main__":
    app = LostvayneControlPanel()
    app.mainloop()