import asyncio
import time
import random
from bs4 import BeautifulSoup
from core.ghost_mode import GhostMode
from core.knowledge import JarvisMemory


class JavaRushSync:
    def __init__(self):
        self.ghost = GhostMode()
        self.memory = JarvisMemory()
        self.base_url = "https://javarush.com"

    async def auto_farm(self, start_url):
        # Перевірка валідності посилання для стабільності
        if not start_url.startswith("http"):
            print("⚠️ Сер, вказане посилання не є валідним.")
            return
        await self.local_collect(start_url)

    async def local_collect(self, url):
        """Сер, збираю контент локально без зайвої активності на сайті"""
        try:
            print(f"🕵️ JARVIS: Тихий збір даних: {url}")
            self.ghost.driver.get(url)
            time.sleep(random.uniform(8, 15))

            soup = BeautifulSoup(self.ghost.driver.page_source, 'html.parser')
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "Без назви"
            content_div = soup.find('div', class_='lecture-content')

            if content_div:
                # Виправив область видимості: запис відбувається тільки якщо контент знайдено
                text_content = content_div.text.strip()
                self.memory.remember('lecture', title, text_content)
                print(f"✅ JARVIS: Локальна копія '{title}' збережена.")
                self.ghost.human_scroll()
            else:
                print("⚠️ Сер, контент лекції не знайдено.")
        except Exception as e:
            print(f"❌ Сер, виникла помилка: {e}")