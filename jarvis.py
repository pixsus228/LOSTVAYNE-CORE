import warnings
import io
import os
import gc  # Коментуй: Додаю модуль для примусового збору сміття
import pyautogui
from PIL import Image

warnings.filterwarnings("ignore")

import telebot
import psutil
import platform
import google.generativeai as genai
import config

bot = telebot.TeleBot(config.BOT_TOKEN)
genai.configure(api_key=config.GEMINI_KEY)

SYSTEM_PROMPT = (
    "Ти — Джарвіс, особистий ШІ Агента Алекса. "
    "Алекс — власник Lenovo LOQ, водій ВАЗ-2111. "
    "Твій стиль: професійний, відданий. Відповідай українською."
)


def is_owner(message):
    return message.from_user.id == config.OWNER_ID


# Використовую модель Flash для швидкості та економії ресурсів
main_model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
chat_session = main_model.start_chat(history=[])


def get_ai_response(user_text, image=None):
    try:
        content = [f"Агент Алекс: {user_text}", image] if image else f"Агент Алекс: {user_text}"
        response = chat_session.send_message(content)
        return response.text
    except Exception as e:
        return f"Сер, виникла помилка зв'язку з ядром: {e}"


@bot.message_handler(commands=['start'], func=is_owner)
def welcome(message):
    bot.reply_to(message, "Протоколи дій активовані. Оптимізація пам'яті включена. 🛡️")


@bot.message_handler(commands=['status'], func=is_owner)
def status(message):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    import datetime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time

    top_procs = sorted(psutil.process_iter(['name', 'memory_info']),
                       key=lambda x: x.info['memory_info'].rss,
                       reverse=True)[:3]

    procs_list = "".join([f"🔹 {p.info['name']}: {p.info['memory_info'].rss // (1024 ** 2)} MB\n" for p in top_procs])

    report = (
        f"--- ДІАГНОСТИКА S.H.I.E.L.D. ---\n"
        f"🖥️ **Хост:** {platform.node()}\n"
        f"⚙️ **Процесор:** {cpu}%\n"
        f"📊 **Пам'ять:** {ram.percent}% ({ram.used // (1024 ** 2)}MB / {ram.total // (1024 ** 2)}MB)\n"
        f"💽 **Диск C:** {disk.percent}% вільно {disk.free // (1024 ** 3)}GB\n"
        f"⏱️ **Аптайм:** {str(uptime).split('.')[0]}\n\n"
        f"🔝 **ТОП ПРОЦЕСІВ:**\n{procs_list}"
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


@bot.message_handler(commands=['reset'], func=is_owner)
def reset_memory(message):
    global chat_session
    chat_session = main_model.start_chat(history=[])
    gc.collect()  # Коментуй: Примусово чищу RAM після скидання пам'яті
    bot.reply_to(message, "🧠 Нейронну мережу перезавантажено.")


@bot.message_handler(content_types=['text', 'photo'], func=is_owner)
def chat(message):
    bot.send_chat_action(message.chat.id, action='typing')
    user_text = message.text or message.caption or "Що на фото?"

    # Коментуй: Використовую безпечну обробку зображень
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Блок 'with' гарантує закриття об'єкта Image відразу після використання
        with Image.open(io.BytesIO(downloaded_file)) as image:
            reply = get_ai_response(user_text, image)
    else:
        reply = get_ai_response(user_text)

    bot.reply_to(message, reply)

    # Коментуй: Після кожного повідомлення змушую систему Python прибрати за собою
    gc.collect()


if __name__ == "__main__":
    print(f"--- [LOG] JARVIS_V2_EVOLUTION (OPTIMIZED) IS OPERATIONAL ---")
    bot.infinity_polling()