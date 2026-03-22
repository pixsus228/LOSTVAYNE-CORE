import asyncio
import sys
import os
from dotenv import load_dotenv
from core.sensors import SystemMonitor
from core.logic import JarvisLogic

class JarvisCore:
    def __init__(self):
        load_dotenv()
        self._verify_env()
        self.monitor = SystemMonitor()
        self.logic = JarvisLogic()
        self.is_active = True

    def _verify_env(self):
        required = ["TG_TOKEN", "GG_API_KEY"]
        if not all(os.getenv(k) for k in required):
            print("❌ Сер, критична помилка: Ключі у .env відсутні.")
            sys.exit(1)
        print("✅ Безпечне з'єднання встановлено.")

    async def handle_input(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, "Я слухаю, Сер >> ")

    async def process_command(self, cmd):
        cmd = cmd.lower().strip()
        if cmd in ["статус", "1"]:
            s = await self.monitor.get_stats()
            print(f"📊 СТАН: CPU: {s['cpu']} | RAM: {s['ram_percent']}%")
        elif cmd in ["очистити", "2"]:
            freed = await self.monitor.optimize_memory()
            print(f"🧹 Вивільнено: {freed} GB, Сер.")
        elif cmd in ["фарм", "3"]:
            from core.jr_sync import JavaRushSync
            url = input("🔗 Сер, вставте посилання на лекцію: ")
            sync = JavaRushSync()
            await sync.auto_farm(url)
        elif cmd in ["вихід", "0"]:
            self.is_active = False
        elif cmd:
            print("🤖 JARVIS думає...")
            response = await self.logic.think(cmd)
            print(f"\n{response}\n")

    async def run(self):
        print("⚡ LOSTVAYNE-CORE АКТИВОВАНО")
        monitor_task = asyncio.create_task(self.monitor.start(interval=60))
        try:
            while self.is_active:
                user_cmd = await self.handle_input()
                await self.process_command(user_cmd)
        finally:
            self.monitor.is_running = False
            monitor_task.cancel()

if __name__ == "__main__":
    jarvis = JarvisCore()
    try:
        asyncio.run(jarvis.run())
    except KeyboardInterrupt:
        print("\nСер, систему вимкнено.")