import sqlite3
import os
import sys

# Сер, налаштував UTF-8 для вашого LOSTVAYNE-LOQ
if sys.platform == "win32":
    os.system('chcp 65001 > nul')
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def search_brain(query):
    # вирахував шлях до бази відносно цього файлу
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'data', 'lostvayne_brain.db')

    if not os.path.exists(db_path):
        print(f"[!] Сер, база не знайдена за шляхом: {db_path}")
        return

    # підключився до пам'яті JARVIS
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # шукаю збіги в заголовках або контенті
    search_query = f"%{query}%"
    cursor.execute('''
                   SELECT level, title, content
                   FROM java_rush_lectures
                   WHERE title LIKE ?
                      OR content LIKE ?
                   ''', (search_query, search_query))

    results = cursor.fetchall()
    conn.close()

    if results:
        print(f"\n[GHOST] Знайшов лекцій: {len(results)}\n" + "=" * 50)
        for level, title, content in results:
            print(f"РІВЕНЬ {level} | {title.upper()}")
            print("-" * 50)
            # виводжу початок конспекту
            summary = content[:600].replace('\n', ' ')
            print(f"{summary}...")
            print("=" * 50 + "\n")
    else:
        print(f"[!] Сер, у моїй базі немає нічого про '{query}'.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # об'єднав аргументи, якщо запит з кількох слів
        search_brain(" ".join(sys.argv[1:]))
    else:
        print("[?] Сер, вкажіть тему. Наприклад: python engine/local_library.py словник")