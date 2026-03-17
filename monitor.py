import psutil
import asyncio
from datetime import datetime


# Створив клас для фонового моніторингу системи LOSTVAYNE-LOQ
class SystemMonitor:
    def __init__(self):
        # Ініціалізував стан монітора
        self.is_running = False

    async def get_stats(self):
        # Зібрав актуальні дані про процесор та пам'ять
        cpu = psutil.cpu_percent(interval=None)  # interval=None для асинхронності
        ram = psutil.virtual_memory()

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu": f"{cpu}%",
            "ram_percent": ram.percent,
            "ram_gb": round(ram.available / (1024 ** 3), 2)
        }

    async def start(self, interval=5):
        # Запустив цикл моніторингу, що не блокує систему
        self.is_running = True
        print("Сер, систему моніторингу активовано.")

        while self.is_running:
            stats = await self.get_stats()

            # Додав логіку сповіщення про перевантаження (Memory Optimization)
            if stats['ram_percent'] > 90:
                print(f"⚠️ УВАГА, Сер! Навантаження на RAM критичне: {stats['ram_percent']}%")

            # Вивів логіку в консоль для тестування
            # print(f"[{stats['time']}] CPU: {stats['cpu']} | RAM: {stats['ram_percent']}%")

            await asyncio.sleep(interval)  # Асинхронна пауза, не фрізить код

    def stop(self):
        # Зупинив процес
        self.is_running = False
        print("Сер, моніторинг переведено в режим очікування.")


# Тестовий запуск ядра монітора
if __name__ == "__main__":
    monitor = SystemMonitor()
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        monitor.stop()