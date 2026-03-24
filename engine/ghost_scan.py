import time
import random
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By

# Додав логування для відстеження помилок у фоні
logging.basicConfig(filename='data/ghost_errors.log', level=logging.ERROR)


def resilient_action(func):
    """Декоратор для повторних спроб при помилках"""

    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except (WebDriverException, Exception) as e:
                wait_time = (attempt + 1) * 5
                print(f"[!] Помилка: {e}. Спроба {attempt + 1}/3 через {wait_time}с...")
                time.sleep(wait_time)
        return None

    return wrapper


@resilient_action
def sync_with_mentor_progress(driver, target_level):
    """Синхронізація: відкриваю рівні, поки не досягну рівня ментора"""
    driver.get(f"https://javarush.com/quests/lectures?level={target_level}")

    # Логіка використання 'темної матерії'
    try:
        unlock_btn = driver.find_element(By.ID, "unlock_next_level_button")
        if unlock_btn.is_enabled():
            unlock_btn.click()
            print("[GHOST] Використав темну матерію. Рівень оновлено.")
    except NoSuchElementException:
        print("[*] Рівень уже розблокований або матерії недостатньо.")


if __name__ == "__main__":
    # Сер, о 19:34 (вівторок) якраз іде заняття.
    # JARVIS готовий заступити на зміну після 21:00.
    pass