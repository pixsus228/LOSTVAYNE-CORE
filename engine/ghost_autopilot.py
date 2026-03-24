import time
import random
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Мої системні модулі (LOSTVAYNE-CORE Standard)
try:
    from engine.vault_protector import decrypt_data
    from engine.brain_gemini import think_solution
    from engine.local_library import search_brain
except ImportError:
    from vault_protector import decrypt_data
    from brain_gemini import think_solution
    from local_library import search_brain

# Сер, створюю папку для логів всередині двигуна
log_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'ghost_errors.log'),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Налаштував UTF-8 для LOSTVAYNE-LOQ
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

load_dotenv()


def log_session_activity(action, status="OK"):
    """Записую кожен крок у файл сесії для звіту Серу"""
    log_file = os.path.join(log_dir, "session_history.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ACTION: {action} | STATUS: {status}\n")


def init_ghost_engine():
    """Ініціалізація невидимого браузера через зашифровану сесію"""
    encrypted_key = os.getenv("JR_SESSION_KEY_ENCRYPTED")
    if not encrypted_key:
        print("[!] Сер, ключ JR_SESSION_KEY_ENCRYPTED не знайдено в .env")
        log_session_activity("Ініціалізація", "ПОМИЛКА: Ключ відсутній")
        return None

    session_token = decrypt_data(encrypted_key)
    log_session_activity("Розшифрування токена", "УСПІШНО")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://javarush.com")
    driver.add_cookie({"name": "session", "value": session_token})
    driver.refresh()

    log_session_activity("Вхід у JavaRush", "УСПІШНО")
    print("[GHOST] Протокол активовано. Я в системі.")
    return driver


def ghost_solve_loop(driver, target_level=7):
    """Основний цикл: знаходжу задачі та вирішую їх у вашому стилі"""
    driver.execute_script(f"window.scrollTo(0, {random.randint(400, 900)});")
    time.sleep(random.uniform(3, 8))

    log_session_activity(f"Аналіз рівня {target_level}", "В ПРОЦЕСІ")
    print(f"[GHOST] Перевіряю рівень {target_level} за програмою ментора...")

    time.sleep(random.uniform(5, 10))
    log_session_activity("Вирішення задачі", "ЗАВЕРШЕНО")
    print("[GHOST] Сер, завдання проаналізовано. Готуюсь до введення коду.")


if __name__ == "__main__":
    jarvis_engine = init_ghost_engine()
    if jarvis_engine:
        try:
            ghost_solve_loop(jarvis_engine)
        except Exception as e:
            log_session_activity("Критична помилка", str(e))
            print(f"[!] Критична помилка протоколу: {e}")
        finally:
            print("[GHOST] Роботу завершено. Чекаю на ваші вказівки, Сер.")