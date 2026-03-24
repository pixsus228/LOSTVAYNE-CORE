import psutil
import asyncio
import gc

class SystemMonitor:
    def __init__(self):
        self.is_running = False

    async def get_stats(self):
        # Зчитую актуальні дані LOQ
        return {
            "cpu": f"{psutil.cpu_percent()}%",
            "ram_percent": psutil.virtual_memory().percent,
            "ram_used": round(psutil.virtual_memory().used / (1024**3), 2)
        }

    async def optimize_memory(self):
        # Примусове очищення
        before = round(psutil.virtual_memory().used / (1024**3), 2)
        gc.collect()
        after = round(psutil.virtual_memory().used / (1024**3), 2)
        return round(before - after, 2)

    async def start(self, interval=60):
        # Фоновий моніторинг
        self.is_running = True
        while self.is_running:
            stats = await self.get_stats()
            if stats['ram_percent'] > 90:
                print(f"⚠️ JARVIS: Критичне навантаження RAM: {stats['ram_percent']}%! Оптимізую...")
                await self.optimize_memory()
            await asyncio.sleep(interval)