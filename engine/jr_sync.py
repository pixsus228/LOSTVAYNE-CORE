import sqlite3
import os
import requests
import sys
from bs4 import BeautifulSoup

# налаштував кодування для термінала Windows
if sys.platform == "win32":
    # примусово ввімкнув UTF-8 в консолі
    os.system('chcp 65001 > nul')
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def init_brain():
    # визначив абсолютний шлях, щоб уникнути помилок доступу
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'data')
    db_path = os.path.join(db_dir, 'lostvayne_brain.db')

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"[GHOST] Створив папку для бази: {db_dir}")

    conn = sqlite3.connect(db_path)
    # створив таблицю з правильними відступами
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS java_rush_lectures
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     level
                     INTEGER,
                     title
                     TEXT,
                     url
                     TEXT
                     UNIQUE,
                     content
                     TEXT
                 )
                 ''')
    conn.commit()
    return conn, db_path


def sync_all_lectures():
    conn, db_path = init_brain()
    cursor = conn.cursor()

    base_url = "https://javarush.com/quests/lectures/ua.javarush.python.core.lecture.level"
    print(f"[GHOST] Починаю повну синхронізацію: {db_path}")

    for lvl in range(8):  # рівні 0-7
        for lec in range(15):
            lvl_str = str(lvl).zfill(2)
            lec_str = str(lec).zfill(2)
            url = f"{base_url}{lvl_str}.lecture{lec_str}"

            try:
                # додав заголовки, щоб сайт не блокував запит
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(url, headers=headers, timeout=5)
                resp.encoding = 'utf-8'  # зафіксував кодування сайту

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"Лекція {lec}"

                    content_div = soup.find('div', class_='lecture-content')
                    content = content_div.get_text(separator='\n', strip=True) if content_div else ""

                    # перезаписую старі криві дані новими
                    cursor.execute('''
                        INSERT OR REPLACE INTO java_rush_lectures (level, title, url, content)
                        VALUES (?, ?, ?, ?)
                    ''', (lvl, title, url, content))

                    print(f"[+] Рівень {lvl}, Лекція {lec}: '{title}' — додано.")
                else:
                    break
            except Exception as e:
                print(f"[!] Помилка на {url}: {e}")
                continue

    conn.commit()
    conn.close()
    print("\n[GHOST] Сер, систему оновлено. Тепер все читабельно.")


if __name__ == "__main__":
    sync_all_lectures()