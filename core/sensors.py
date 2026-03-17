import psutil
import asyncio
import gc # Гарантоване очищення пам'яті Python
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.is_running = False

    async def get_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            return {
                "cpu": f"{cpu}%",
                "ram_percent": ram.percent,
                "ram_gb": round(ram.available / (1024**3), 2)
            }
        except Exception as e:
            return {"error": str(e)}

    async def optimize_memory(self):
        # Додав примусовий збір сміття
        before = psutil.virtual_memory().available / (1024**3)
        gc.collect()
        after = psutil.virtual_memory().available / (1024**3)
        # Записав результат оптимізації
        return round(after - before, 2)

    async def start(self, interval=10):
        self.is_running = True
        while self.is_running:
            stats = await self.get_stats()
            if "error" not in stats and stats['ram_percent'] > 85:
                print(f"⚠️ Сер, RAM: {stats['ram_percent']}%. Оптимізую...")
                freed = await self.optimize_memory()
                print(f"✅ Очищено {freed} GB.")
            await asyncio.sleep(interval)