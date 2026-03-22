import time
import random
import undetected_chromedriver as uc

class GhostMode:
    def __init__(self):
        self.driver = uc.Chrome()

    def human_scroll(self):
        height = self.driver.execute_script("return document.body.scrollHeight")
        curr = 0
        while curr < height:
            curr += random.randint(300, 600)
            self.driver.execute_script(f"window.scrollTo(0, {curr});")
            time.sleep(random.uniform(2.5, 6.0))

    def close(self):
        self.driver.quit()