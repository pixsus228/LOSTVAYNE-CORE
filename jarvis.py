import asyncio
import sys
import os
from dotenv import load_dotenv
from core.sensors import SystemMonitor
from core.ghost_mode import GhostMode

class JarvisCore:
    def __init__(self):
        load_dotenv()
        self._безпечний_старт()
        self._create_desktop_bat() # Авто-створення ярлика запуску
        self.monitor = SystemMonitor()
        self.ghost = None
        self.is_active = True

    def _create_desktop_bat(self):
        """Створюю START_JARVIS.bat на Вашому робочому столі для запуску одним кліком"""
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        bat_path = os.path.join(desktop, "START_JARVIS.bat")
        project_dir = os.path.dirname(os.path.abspath(__file__))
        python_exe = sys.executable
        content = f"""@echo off\ncls\ntitle JARVIS - {os.path.basename(project_dir)}\ncd /d "{project_dir}"\n"{python_exe}" jarvis.py\npause"""
        try:
            with open(bat_path, "w", encoding="cp1251") as f: f.write(content)
            print("✅ Сер, ярлик START_JARVIS.bat створено на робочому столі.")
        except: pass

    def _безпечний_старт(self):
        if not os.getenv("GG_API_KEY"):
            print("❌ Сер, критична помилка: .env файл не налаштовано.")
            sys.exit(1)
        print("✅ Безпечне з'єднання встановлено. JARVIS готовий.")

    async def handle_input(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, "Я слухаю, Сер (3 - навчання, 0 - вихід) >> ")

    async def process_command(self, cmd):
        cmd = cmd.lower().strip()
        if cmd in ["статус", "1"]:
            s = await self.monitor.get_stats()
            print(f"📊 Стан LOQ: CPU {s['cpu']}% | RAM {s['ram_percent']}%")
        elif cmd in ["навчання", "3", "фарм"]:
            print("🚀 Запускаю автономний Ghost-цикл...")
            self.ghost = GhostMode()
            if self.ghost.driver:
                await asyncio.to_thread(self._почав_вчитися)
            else: self.ghost = None
        elif cmd in ["вихід", "0"]: self.is_active = False

    def _почав_вчитися(self):
        try:
            self.ghost.driver.get("https://javarush.com/quests")
            self.ghost.automate_learning_cycle()
        except Exception as e: print(f"⚠️ Перервано: {e}")
        finally:
            if self.ghost: self.ghost.close(); self.ghost = None

    async def run(self):
        print("⚡ LOSTVAYNE-CORE ОНЛАЙН.")
        monitor_task = asyncio.create_task(self.monitor.start(interval=60))
        try:
            while self.is_active:
                user_cmd = await self.handle_input()
                await self.process_command(user_cmd)
        finally:
            self.monitor.is_running = False
            if self.ghost: self.ghost.close()
            monitor_task.cancel()
            print("🔒 Система вимкнена. Гарного відпочинку, Сер.")

if __name__ == "__main__":
    asyncio.run(JarvisCore().run())