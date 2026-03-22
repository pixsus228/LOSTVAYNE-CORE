import sqlite3
import os
from datetime import datetime

class JarvisMemory:
    def __init__(self, db_path="data/lostvayne_brain.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._setup_tables()

    def _setup_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT, content TEXT, source TEXT, timestamp DATETIME
            )
        ''')
        self.conn.commit()

    def remember(self, topic, content, source="JavaRush"):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO experience VALUES (NULL, ?, ?, ?, ?)',
                       (topic, content, source, datetime.now()))
        self.conn.commit()
        print(f"✅ Сер, знання про '{topic}' зафіксовані.")