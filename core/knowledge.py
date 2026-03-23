import sqlite3
import os

class LostvayneBrain:
    def __init__(self, db_path: str = "data/lostvayne_brain.db"):
        self.db_path = db_path
        # Створив папку data, якщо вона відсутня
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        """Сер, ініціалізую таблиці для Ваших знань"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS lectures 
                    (id INTEGER PRIMARY KEY, title TEXT, content TEXT, date TEXT)
                """)
        except sqlite3.Error as e:
            # Записав помилку в консоль, щоб Ви були в курсі
            print(f"⚠️ Сер, виникла помилка БД: {e}")

    def remember(self, title, content):
        """Записав лекцію в пам'ять системи"""
        from datetime import datetime
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO lectures (title, content, date) VALUES (?, ?, ?)",
                    (title, content, datetime.now().strftime("%Y-%m-%d %H:%M"))
                )
            print(f"✅ JARVIS: Лекцію '{title}' зафіксовано.")
        except Exception as e:
            print(f"❌ Сер, не зміг запам'ятати: {e}")

    @staticmethod
    def пишу_код_руками():
        print("Сер, код пишеться згідно з вашими стандартами.")