import sqlite3
import os
import shutil
from datetime import datetime

class JarvisMemory:
    def __init__(self, db_path="data/lostvayne_brain.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._setup_tables()

    def _setup_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS experience 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, topic TEXT, content TEXT, timestamp DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS progress 
            (planet TEXT PRIMARY KEY, level INTEGER, last_sync DATETIME)''')
        self.conn.commit()

    def make_backup(self):
        # Сер, реалізував метод бекапу, якого не вистачало
        backup_dir = "backups/db"
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%m%d_%H%M")
        shutil.copy2(self.db_path, f"{backup_dir}/brain_{ts}.db")
        print(f"📦 JARVIS: Резервну копію ядра створено.")

    def remember(self, data_type, topic, content):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO experience (type, topic, content, timestamp) VALUES (?, ?, ?, ?)',
                       (data_type, topic, content, datetime.now()))
        self.conn.commit()
        print(f"✅ JARVIS: Знання про '{topic}' зафіксовані.")

    def update_progress(self, planet, level):
        self.make_backup()
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO progress VALUES (?, ?, ?)', (planet, level, datetime.now()))
        self.conn.commit()
        print(f"🚀 JARVIS: Прогрес на {planet} оновлено до {level} рівня.")