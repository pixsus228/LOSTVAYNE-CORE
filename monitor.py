import psutil
import tkinter as tk


def show_status_overlay():
    # 1. Збір метрик LOSTVAYNE-LOQ
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    bat = psutil.sensors_battery()

    # Логіка відображення живлення
    if bat:
        pwr = f"🔌 {bat.percent}%" if bat.power_plugged else f"🔋 {bat.percent}%"
    else:
        pwr = "🔌 AC POWER"

    # 2. Створення UI
    overlay = tk.Tk()
    overlay.attributes("-topmost", True)  # Поверх усіх вікон
    overlay.attributes("-alpha", 0.85)  # Напівпрозорість
    overlay.overrideredirect(True)  # Без рамок Windows

    # Позиціонування: зверху справа (підберіть під свій монітор)
    # Формат: "ШиринаxВисота+X+Y"
    overlay.geometry("220x60+1650+30")
    overlay.configure(bg='#0a0a0a')

    # Текст у стилі термінала S.H.I.E.L.D.
    display_text = f"CPU: {cpu}% | RAM: {ram}%\nPWR: {pwr}\n[MARK-4.0 ACTIVE]"
    label = tk.Label(overlay, text=display_text, fg="#00FF41", bg="#0a0a0a", font=("Consolas", 9, "bold"))
    label.pack(expand=True)

    # Функції для перетягування вікна
    def _start_drag(event):
        overlay._x = event.x
        overlay._y = event.y

    def _on_drag(event):
        deltax = event.x - overlay._x
        deltay = event.y - overlay._y
        x = overlay.winfo_x() + deltax
        y = overlay.winfo_y() + deltay
        overlay.geometry(f"+{x}+{y}")

    # Прив'язка подій миші до вікна (або до label, що покриває вікно)
    label.bind("<ButtonPress-1>", _start_drag)
    label.bind("<B1-Motion>", _on_drag)

    # 3. Самознищення через 5000 мс (5 сек)
    overlay.after(5000, overlay.destroy)
    overlay.mainloop()


if __name__ == "__main__":
    show_status_overlay()