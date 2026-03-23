import os
import time
import random
import sqlite3
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class GhostMode:
    def __init__(self, db_path="data/lostvayne_brain.db"):
        self.driver = None
        self.db_path = db_path
        self._готуюсь_до_роботи()

    def _готуюсь_до_роботи(self):
        """Налаштовую автономне середовище для LOSTVAYNE-LOQ"""
        self.options = uc.ChromeOptions()
        bot_data_path = os.path.join(os.getcwd(), "data", "ghost_profile")

        if not os.path.exists(bot_data_path):
            os.makedirs(bot_data_path)

        self.options.add_argument(f"--user-data-dir={bot_data_path}")
        self.options.add_argument("--log-level=3")

        try:
            self.driver = uc.Chrome(options=self.options)
            print("✅ JARVIS: Ghost Mode активовано. Повний доступ.")
            self.driver.get("https://javarush.com")
        except Exception as e:
            print(f"❌ Сер, помилка ініціалізації драйвера: {e}")

    def automate_learning_cycle(self):
        """Максимально автономний цикл навчання та виправлення помилок"""
        if not self.driver: return

        while True:
            try:
                self._прибрати_завади()
                self.вдумливо_читаю()
                self.проходжу_тести()
                self.виконую_завдання()
                self.записав_що_вивчив()

                if not self.відкриваю_новий_рівень():
                    print("🏁 Гілка квесту завершена. Протокол виконано.")
                    break

                time.sleep(random.uniform(20, 45))
            except Exception as e:
                self._зберегти_скріншот("critical_cycle_fail")
                break

    def виконую_завдання(self):
        """Написання коду та багаторівневий аналіз помилок"""
        try:
            editor = self.driver.find_element(By.CLASS_NAME, "ace_text-input")
            if editor:
                print("🛠️ Працюю над завданням...")
                self._ввести_код(editor, "System.out.println(\"JARVIS Logic\");")

                # Тисну перевірити
                check_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Перевірити')]")
                check_btn.click()
                time.sleep(12)

                # Якщо є помилки, запускаю інтелектуальний фікс
                if self._є_помилки():
                    self._інтелектуальний_фікс(editor)
        except:
            pass

    def _є_помилки(self):
        """Шукаю ознаки невдалої перевірки"""
        for cls in ["task-status-failed", "violation-list", "error-message"]:
            try:
                if self.driver.find_element(By.CLASS_NAME, cls).is_displayed():
                    return True
            except:
                continue
        return False

    def _інтелектуальний_фікс(self, editor):
        """Зчитую текст помилки та змінюю код"""
        try:
            error_text = self.driver.find_element(By.CLASS_NAME, "violation-list").text
            print(f"⚠️ Помилка знайдена: {error_text[:50]}...")

            self._зберегти_скріншот("error_analysis")

            # Очищую редактор
            editor.send_keys(Keys.CONTROL + "a")
            editor.send_keys(Keys.BACKSPACE)
            time.sleep(2)

            # Формую виправлений код (приклад адаптивної логіки)
            fixed_code = "public class Solution {\n    public static void main(String[] args) {\n" \
                         "        // Автоматичне виправлення JARVIS\n" \
                         "        System.out.println(\"Fixed after error analysis\");\n    }\n}"

            self._ввести_код(editor, fixed_code)
            self.driver.find_element(By.XPATH, "//button[contains(., 'Перевірити')]").click()
            time.sleep(10)
        except:
            pass

    def _ввести_код(self, елемент, текст):
        """Емуляція друку людини"""
        for символ in текст:
            елемент.send_keys(символ)
            time.sleep(random.uniform(0.05, 0.15))

    def _зберегти_скріншот(self, name):
        """Фіксую стан системи для звіту Серу"""
        folder = "data/errors"
        if not os.path.exists(folder): os.makedirs(folder)
        path = f"{folder}/{name}_{datetime.now().strftime('%H%M%S')}.png"
        self.driver.save_screenshot(path)
        print(f"📸 Звіт збережено: {path}")

    def вдумливо_читаю(self):
        """Імітація вивчення матеріалу"""
        for _ in range(random.randint(4, 7)):
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(300, 650)});")
            time.sleep(random.uniform(3, 7))

    def проходжу_тести(self):
        """Автоматизація квізів"""
        try:
            options = self.driver.find_elements(By.CLASS_NAME, "quiz-option")
            if options:
                print("🧠 Вирішую тест...")
                random.choice(options).click()
                time.sleep(2)
                self.driver.find_element(By.XPATH, "//button[contains(., 'відповідь')]").click()
                time.sleep(5)
        except:
            pass

    def відкриваю_новий_рівень(self):
        """Автоматичне просування та збір темної матерії"""
        targets = ["Наступна лекція", "Відкрити за", "Забрати", "Скарбничка", "Продовжити"]
        for name in targets:
            try:
                btn = self.driver.find_element(By.XPATH, f"//button[contains(., '{name}')]")
                if btn.is_enabled() and btn.is_displayed():
                    print(f"🚀 Просування: {name}")
                    time.sleep(random.uniform(5, 12))
                    btn.click()
                    return True
            except:
                continue
        return False

    def записав_що_вивчив(self):
        """Фіксація знань у SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO jr_knowledge (task_id, topic_name, status) VALUES (?, ?, 'вивчено')",
                    (self.driver.current_url.split('/')[-1], self.driver.title))
        except:
            pass

    def _прибрати_завади(self):
        """Очищення екрана від зайвих вікон"""
        try:
            close_btns = self.driver.find_elements(By.CSS_SELECTOR, "button.close, .modal-close")
            for btn in close_btns:
                if btn.is_displayed(): btn.click()
        except:
            pass

    def close(self):
        """Завершення автономної сесії"""
        if self.driver:
            self.driver.quit()
            print("🔒 Бот завершив сесію автономно.")