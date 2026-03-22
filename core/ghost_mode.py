import os
import time
import undetected_chromedriver as uc


class GhostMode:
    def __init__(self):
        self.options = uc.ChromeOptions()

        # Шлях до Вашого профілю на LOSTVAYNE-LOQ
        user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        self.options.add_argument(f"--user-data-dir={user_data}")
        self.options.add_argument("--profile-directory=Default")

        # Вимикаємо зайві сповіщення
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--no-first-run")

        try:
            self.driver = uc.Chrome(options=self.options)
        except Exception as e:
            print(f"❌ Сер, помилка: Закрийте всі вікна Chrome перед запуском! ({e})")

    def human_scroll(self):
        # Імітую скрол
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")