import telebot
import os
import pyautogui
import psutil
import webbrowser
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# --- МОЯ КОНФІГУРАЦІЯ БЕЗПЕКИ ---
TOKEN = '8693023298:AAGSblENVjQnZZiO_vFn3aSyZAwaXd3cltw'
MY_ID = 718094797
# Мій секретний пароль для прямого доступу з телефону
SECRET_KEY = "Shield_Agent_Alex_77"

bot = telebot.TeleBot(TOKEN)


# --- МОЯ ГОЛОВНА ЛОГІКА ОБРОБКИ КОМАНД ---
def process_jarvis_logic(cmd, chat_id=None):
    """
    Тут я обробляю всі вхідні текстові команди,
    незалежно від того, прийшли вони з Telegram чи через HTTP.
    """
    cmd = cmd.lower().strip()
    print(f" [!] JARVIS ВИКОНУЄ: {cmd}")

    # Перевірка стану мого Lenovo LOQ
    if "статус" in cmd:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        report = f"🖥 **СТАТУС ТЕРМІНАЛУ:**\nПроцесор: {cpu}%\nОЗП: {ram}%"
        if chat_id: bot.send_message(chat_id, report)
        return report

    # Моя команда для дистанційного фото екрана
    elif "скріншот" in cmd or "фото" in cmd:
        img = "shield_snap.png"
        pyautogui.screenshot(img)
        if chat_id:
            with open(img, "rb") as photo:
                bot.send_photo(chat_id, photo)
        os.remove(img)  # Видаляю файл після відправки, щоб не засмічувати пам'ять
        return "Знімок надіслано"

    # Мій швидкий запуск робочого середовища
    elif "запуск" in cmd:
        webbrowser.open("https://www.google.com")
        if chat_id: bot.send_message(chat_id, "Системи готові до роботи.")
        return "Браузер відкрито"

    # Переведення ноутбука в режим сну
    elif "сон" in cmd:
        if chat_id: bot.send_message(chat_id, "Термінал переходить у режим сну. До зв'язку.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Сон"

    return "Команду прийнято"


# --- МІЙ ПРЯМИЙ КАНАЛ (HTTP SERVER) З ФІЛЬТРОМ КЛЮЧА ---
class SecureCommandHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Я приймаю HTTP-запити від MacroDroid.
        Першим ділом перевіряю секретний ключ 'key'.
        """
        query = urlparse(self.path).query
        params = parse_qs(query)
        received_key = params.get("key", [None])[0]

        # Якщо ключ не збігається — я миттєво закриваю з'єднання
        if received_key != SECRET_KEY:
            self.send_response(403)  # Доступ заборонено
            self.end_headers()
            print(f" [!!!] СПРОБА ЗЛАМУ: Невірний ключ від {self.client_address[0]}")
            return

        # Якщо ключ вірний — виконую команду з параметра 'text'
        if "text" in params:
            command_text = params["text"][0]
            process_jarvis_logic(command_text, MY_ID)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")


def run_server():
    """ Я запускаю сервер на порту 5000, щоб телефон міг до мене достукатися """
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, SecureCommandHandler)
    print(" [S] ПРЯМИЙ КАНАЛ (UPLINK) ВІДКРИТО: Port 5000")
    httpd.serve_forever()


# --- МОЯ СЛУЖБА ТЕЛЕГРАМ З АВТОВІДНОВЛЕННЯМ ---
def run_telegram_bot():
    """
    Цей цикл дозволяє мені автоматично перепідключатися до Telegram,
    якщо інтернет раптом зникне або сервер видасть помилку.
    """
    while True:
        try:
            print("... Джарвіс слухає Telegram-ефір ...")
            bot.polling(none_stop=True, interval=2, timeout=60)
        except Exception as e:
            print(f" [!] ЗБІЙ ЗВ'ЯЗКУ: {e}. Перезапуск через 5 сек...")
            time.sleep(5)


# --- ТОЧКА ЗАПУСКУ ВСІХ СИСТЕМ ---
if __name__ == '__main__':
    print("\n" + "=" * 40)
    print("--- [JARVIS: ГОЛОВНА ГІЛКА (MASTER) ЗАПУЩЕНА] ---")
    print("=" * 40)

    # Я запускаю сервер у фоновому потоці (daemon)
    Thread(target=run_server, daemon=True).start()

    # Я запускаю бота в основному потоці
    run_telegram_bot()