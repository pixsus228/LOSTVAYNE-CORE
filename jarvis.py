import asyncio
import sys
# 1. Виправив шлях імпорту до ваших "сенсорів"
from core.sensors import SystemMonitor

class JarvisCore:
    def __init__(self):
        # Ініціалізував монітор з нової структури
        self.monitor = SystemMonitor()
        self.is_active = True

    async def handle_input(self):
        # Зробив ввід неблокуючим для консолі LOSTVAYNE-LOQ
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, "Я слухаю, Сер >> ")

    async def process_command(self, cmd):
        cmd = cmd.lower().strip()

        if cmd in ["статус", "status", "1"]:
            s = await self.monitor.get_stats()
            # Вивів актуальні дані про залізо
            print(f"📊 СТАН: CPU: {s['cpu']} | RAM: {s['ram_percent']}% (Вільна: {s['ram_gb']} GB)")

        elif cmd in ["очистити", "optimize", "2"]:
            # Викликав метод оптимізації, який ми прописали в sensors.py
            freed = await self.monitor.optimize_memory()
            print(f"🧹 Оптимізація завершена. Вивільнено: {freed} GB, Сер.")

        elif cmd in ["вихід", "exit", "0"]:
            self.is_active = False
            print("🔴 Систему вимкнено. Гарного дня, Сер.")

        elif not cmd:
            pass
        else:
            # Тут ми пізніше підключимо core/logic.py для інтелектуальних відповідей
            print(f"❓ Команда '{cmd}' не розпізнана. Чекаю на наступні вказівки.")

    async def run(self):
        print("⚡ LOSTVAYNE-CORE АКТИВОВАНО")
        # Запустив моніторинг окремим таском у фоні
        monitor_task = asyncio.create_task(self.monitor.start(interval=60))

        try:
            while self.is_active:
                user_cmd = await self.handle_input()
                await self.process_command(user_cmd)
        finally:
            # Коректно зупинив усі процеси
            self.monitor.is_running = False
            monitor_task.cancel()
            print("Сер, системи переведено в режим очікування.")

if __name__ == "__main__":
    jarvis = JarvisCore()
    try:
        asyncio.run(jarvis.run())
    except KeyboardInterrupt:
        sys.exit(0)