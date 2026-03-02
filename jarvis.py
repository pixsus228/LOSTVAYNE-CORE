import warnings
import io
import os
import gc
import pyautogui
from PIL import Image

warnings.filterwarnings("ignore")

import telebot
import psutil
import platform
import google.generativeai as genai
import config

# Ініціалізація систем
bot = telebot.TeleBot(config.BOT_TOKEN)
genai.configure(api_key=config.GEMINI_KEY)

SYSTEM_PROMPT = (
    "Ти — Джарвіс, особистий ШІ Агента Алекса. "
    "Алекс — власник Lenovo LOQ, водій ВАЗ-2111. "
    "Твій стиль: професійний, відданий. Відповідай українською."
)

def is_owner(message):
    return message.from_user.id == config.OWNER_ID

# Ініціалізація ядра Gemini
main_model = genai.GenerativeModel('models/gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
chat_session = main_model.start_chat(history=[])

# --- ІНТЕРФЕЙС КНОПОК (REPLY KEYBOARD) ---

def get_main_keyboard():
    """Створюю зручну панель кнопок для керування LOQ."""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Формую сітку кнопок 2x2 для зручності великого пальця
    btn_status = telebot.types.KeyboardButton('📊 СТАТУС')
    btn_screen = telebot.types.KeyboardButton('📸 СКРІНШОТ')
    btn_vol_up = telebot.types.KeyboardButton('🔊 ГУЧНІСТЬ +')
    btn_vol_down = telebot.types.KeyboardButton('🔉 ГУЧНІСТЬ -')
    
    markup.row(btn_status, btn_screen)
    markup.row(btn_vol_up, btn_vol_down)
    
    return markup

# --- РЕЄСТРАЦІЯ ШВИДКОГО МЕНЮ (BLUE BUTTON) ---

def set_main_menu(bot):
    """Реєструю команди в синій кнопці 'Menu'."""
    commands = [
        telebot.types.BotCommand("/status", "📊 Статус системи"),
        telebot.types.BotCommand("/screen", "📸 Скріншот"),
        telebot.types.BotCommand("/volup", "🔊 Гучність +"),
        telebot.types.BotCommand("/voldown", "🔉 Гучність -"),
        telebot.types.BotCommand("/sleep", "🌙 Сон"),
        telebot.types.BotCommand("/shutdown", "🚨 Вимкнути ПК")
    ]
    # Відправляю список команд на сервери Telegram
    bot.set_my_commands(commands)


def get_ai_response(user_text, image=None):
    """Отримую відповідь від ШІ, враховуючи текстові та візуальні дані."""
    try:
        content = [f"Агент Алекс: {user_text}", image] if image else f"Агент Алекс: {user_text}"
        response = chat_session.send_message(content)
        return response.text
    except Exception as e:
        # Активуваю резервну лінію (старий надійний gemini-pro) у разі збою
        try:
            print(f"--- [WARN] Основна лінія недоступна ({e}). Перемикаюсь на резерв... ---")
            # Використовую gemini-pro (1.0) як найнадійніший варіант для бекапу
            model = genai.GenerativeModel('models/gemini-pro', system_instruction=SYSTEM_PROMPT)
            if image:
                return "[РЕЗЕРВНИЙ КАНАЛ] Сер, резервна лінія застаріла і не підтримує аналіз зображень. Тільки текст."
            
            response = model.generate_content(f"Агент Алекс: {user_text}")
            return f"[РЕЗЕРВНИЙ КАНАЛ] {response.text}"
        except Exception as e_backup:
            # Виводжу звіт про критичну ізоляцію термінала від мережі
            return f"Сер, системи Google відмовили у доступі. Основна помилка: {e}. Резервна: {e_backup}"

# --- БАЗОВІ КОМАНДИ ---

@bot.message_handler(commands=['start'], func=is_owner)
def welcome(message):
    """Протокол ініціалізації: активую всі системи та виводжу панель керування."""
    bot.reply_to(
        message, 
        "Протоколи дій активовані. Панель керування LOQ виведена на Ваш термінал, сер. 🛡️",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['status'], func=is_owner)
def status(message):
    """Виконую повну діагностику ресурсів LOQ."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    import datetime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()) # type: ignore
    uptime = datetime.datetime.now() - boot_time

    top_procs = sorted(psutil.process_iter(['name', 'memory_info']),
                       key=lambda x: x.info['memory_info'].rss, reverse=True)[:3]
    procs_list = "".join([f"🔹 {p.info['name']}: {p.info['memory_info'].rss // (1024 ** 2)} MB\n" for p in top_procs])

    report = (
        f"--- ДІАГНОСТИКА S.H.I.E.L.D. ---\n"
        f"🖥️ **Хост:** {platform.node()}\n"
        f"⚙️ **Процесор:** {cpu}%\n"
        f"📊 **Пам'ять:** {ram.percent}% ({ram.used // (1024 ** 2)}MB)\n"
        f"💽 **Диск C:** {disk.percent}% (вільно {disk.free // (1024 ** 3)}GB)\n"
        f"⏱️ **Аптайм:** {str(uptime).split('.')[0]}\n\n"
        f"🔝 **ТОП ПРОЦЕСІВ:**\n{procs_list}" # type: ignore
    )
    bot.reply_to(message, report, parse_mode='Markdown')

@bot.message_handler(commands=['screen'], func=is_owner)
def take_screenshot(message):
    bot.send_chat_action(message.chat.id, action='upload_photo')
    screen_path = "temp_screen.png"
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(screen_path)
        with open(screen_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="📸 Звіт візуального контролю, сер.")
        os.remove(screen_path)
    except Exception as e:
        bot.reply_to(message, f"🚨 Помилка: {e}")

# --- ПРОТОКОЛ "МЕДІА" (ЗВУК) ---

@bot.message_handler(commands=['volup'], func=is_owner)
def volume_up(message):
    for _ in range(5): pyautogui.press('volumeup')
    bot.reply_to(message, "🔊 Гучність збільшено.")

@bot.message_handler(commands=['voldown'], func=is_owner)
def volume_down(message):
    for _ in range(5): pyautogui.press('volumedown')
    bot.reply_to(message, "🔉 Гучність зменшено.")

@bot.message_handler(commands=['mute'], func=is_owner)
def volume_mute(message):
    pyautogui.press('volumemute')
    bot.reply_to(message, "🔇 Стан звуку змінено.")

# --- ПРОТОКОЛ "ЕНЕРГІЯ" (ЖИВЛЕННЯ) ---

@bot.message_handler(commands=['sleep'], func=is_owner)
def system_sleep(message):
    bot.reply_to(message, "🌙 Перевожу LOQ у режим сну. До зв'язку, сер.")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

@bot.message_handler(commands=['shutdown'], func=is_owner)
def system_shutdown(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("ТАК", callback_data="confirm_sd"),
               telebot.types.InlineKeyboardButton("НІ", callback_data="cancel_sd"))
    bot.send_message(message.chat.id, "🚨 Ви впевнені, що хочете ВИМКНУТИ систему?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_sd", "cancel_sd"])
def handle_sd_confirm(call):
    if call.data == "confirm_sd":
        bot.edit_message_text("☢️ Вимикаю систему. Прощавайте, сер.", call.message.chat.id, call.message.message_id)
        os.system("shutdown /s /t 1")
    else:
        bot.edit_message_text("✅ Операцію скасовано.", call.message.chat.id, call.message.message_id)

# --- УПРАВЛІННЯ ПАМ'ЯТТЮ ---

@bot.message_handler(commands=['reset'], func=is_owner)
def reset_memory(message):
    """Очищення буфера пам'яті нейромережі."""
    global chat_session
    chat_session = main_model.start_chat(history=[])
    gc.collect()
    bot.reply_to(message, "🧠 Нейронну мережу перезавантажено.")

# --- ОБРОБКА КНОПОК REPLY KEYBOARD ---

@bot.message_handler(func=lambda message: is_owner(message) and message.text in ['📊 СТАТУС', '📸 СКРІНШОТ', '🔊 ГУЧНІСТЬ +', '🔉 ГУЧНІСТЬ -'])
def handle_keyboard_buttons(message):
    if message.text == '📊 СТАТУС':
        status(message)
    elif message.text == '📸 СКРІНШОТ':
        take_screenshot(message)
    elif message.text == '🔊 ГУЧНІСТЬ +':
        volume_up(message)
    elif message.text == '🔉 ГУЧНІСТЬ -':
        volume_down(message)

# --- ЧАТ З ДЖАРВІСОМ ---

@bot.message_handler(content_types=['text', 'photo'], func=is_owner)
def chat(message):
    bot.send_chat_action(message.chat.id, action='typing')
    user_text = message.text or message.caption or "Що на фото?"
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with Image.open(io.BytesIO(downloaded_file)) as image:
            reply = get_ai_response(user_text, image)
    else:
        reply = get_ai_response(user_text)
    bot.reply_to(message, reply)
    gc.collect()

if __name__ == "__main__":
    set_main_menu(bot)  # Активую інтерфейс меню перед запуском протоколів зв'язку.
    print(f"--- [LOG] JARVIS_V2_EVOLUTION (FULL INTERFACE) IS OPERATIONAL ---")
    bot.infinity_polling()