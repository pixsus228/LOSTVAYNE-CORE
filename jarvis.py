import warnings
import io
import os
import json
import datetime
import gc
import sys
import requests
import pyautogui
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image
from gtts import gTTS
import pygame
import time # Додано імпорт time

warnings.filterwarnings("ignore")

import telebot
import psutil
import platform
import google.generativeai as genai
import config

# Ініціалізація систем
bot = telebot.TeleBot(config.BOT_TOKEN)
genai.configure(api_key=config.GEMINI_KEY)

# --- ЛОКАЛЬНА ПАМ'ЯТЬ (JSON) ---
BRAIN_FILE = "jarvis_brain.json"


def save_to_brain(key, value):
    data = {}
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    data[key] = value
    with open(BRAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_from_brain():
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_current_timestamp():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M")


SYSTEM_PROMPT = (
    "Ти — Джарвіс, особистий ШІ Агента Алекса. "
    "Алекс — власник Lenovo LOQ, водій ВАЗ-2111. "
    "Твій стиль: професійний, відданий. Відповідай українською."
)


def is_owner(message):
    return message.from_user.id == config.OWNER_ID


# Ініціалізація ядра Gemini 2.5 Flash
main_model = genai.GenerativeModel('models/gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
chat_session = main_model.start_chat(history=[])


# --- ІНТЕРФЕЙС ---

def get_main_keyboard():
    """Створюю розширену панель кнопок для керування LOQ."""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(telebot.types.KeyboardButton('📊 СТАТУС'), telebot.types.KeyboardButton('📸 СКРІНШОТ'))
    markup.row(telebot.types.KeyboardButton('🔊 ГУЧНІСТЬ +'), telebot.types.KeyboardButton('🔉 ГУЧНІСТЬ -'))
    markup.row(telebot.types.KeyboardButton('🌤️ ПОГОДА'), telebot.types.KeyboardButton('🧹 DEEP CLEAN'))
    return markup


def set_main_menu(bot):
    """Реєструю повний перелік команд у меню швидкого доступу."""
    commands = [
        telebot.types.BotCommand("/status", "📊 Статус системи"),
        telebot.types.BotCommand("/brain", "🧠 Пам'ять"),
        telebot.types.BotCommand("/weather", "🌤️ Погода Ромни"),
        telebot.types.BotCommand("/screen", "📸 Скріншот"),
        telebot.types.BotCommand("/volup", "🔊 Гучніше"),
        telebot.types.BotCommand("/voldown", "🔉 Тихіше"),
        telebot.types.BotCommand("/mute", "🔇 Вимкнути звук"),
        telebot.types.BotCommand("/deepclean", "🧹 Глибока очистка"),
        telebot.types.BotCommand("/reset", "🧠 Перезавантажити ШІ"),
        telebot.types.BotCommand("/menu", "🔄 Оновити меню"),
        telebot.types.BotCommand("/sleep", "🌙 Сон (Win)"),
        telebot.types.BotCommand("/shutdown", "🚨 Вимкнути ПК")
    ]
    bot.set_my_commands(commands)


def get_ai_response(user_text, image=None):
    """Отримую відповідь з основним та резервним каналами."""
    try:
        content = [f"Агент Алекс: {user_text}", image] if image else f"Агент Алекс: {user_text}"
        response = chat_session.send_message(content)
        return response.text
    except Exception as e:
        try:
            print(f"--- [WARN] Збій 2.5 Flash. Перехід на резерв... ---")
            backup_model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
            content = [f"Агент Алекс: {user_text}", image] if image else f"Агент Алекс: {user_text}"
            response = backup_model.generate_content(content)
            return f"[РЕЗЕРВНИЙ КАНАЛ]\n{response.text}"
        except Exception as e_backup:
            return f"🚨 Критична відмова: {e_backup}"


# --- КОМАНДИ ---

@bot.message_handler(commands=['status'], func=is_owner)
def status(message):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    top_procs = sorted(psutil.process_iter(['name', 'memory_info']), key=lambda x: x.info['memory_info'].rss,
                       reverse=True)[:3]
    procs_list = "".join([f"🔹 {p.info['name']}: {p.info['memory_info'].rss // (1024 ** 2)} MB\n" for p in top_procs])

    report = (
        f"--- ДІАГНОСТИКА S.H.I.E.L.D. ---\n"
        f"🖥️ **Хост:** {platform.node()}\n"
        f"⚙️ **Процесор:** {cpu}%\n"
        f"📊 **Пам'ять:** {ram.percent}% ({ram.used // (1024 ** 2)}MB)\n"
        f"💽 **Диск C:** {disk.percent}% (вільно {disk.free // (1024 ** 3)}GB)\n"
        f"⏱️ **Аптайм:** {str(uptime).split('.')[0]}\n\n"
        f"🔝 **ТОП ПРОЦЕСІВ:**\n{procs_list}"
    )
    bot.reply_to(message, report, parse_mode='Markdown')


@bot.message_handler(commands=['weather'], func=is_owner)
def get_weather(message):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Romny&appid={config.WEATHER_KEY}&units=metric&lang=ua" # Changed to HTTPS
    try:
        res = requests.get(url).json()
        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        report = f"🌤️ **Погода в Ромнах:** {temp}°C, {desc.capitalize()}\nСер, погодні умови стабільні."
        bot.reply_to(message, report, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"🚨 Помилка метео-каналу: {e}")


# --- ГОЛОСОВИЙ МОДУЛЬ (SPEECH-TO-TEXT) ---

@bot.message_handler(content_types=['voice'], func=is_owner)
def handle_voice(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        ogg_path, wav_path = "voice.ogg", "voice.wav"

        with open(ogg_path, 'wb') as f:
            f.write(downloaded_file)

        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="uk-UA")

        response = get_ai_response(text)
        bot.reply_to(message, f"🎤 Ви сказали: \"{text}\"\n\n🤖 {response}")
        
        # ДОДАНО: Виклик speak_and_send для голосової відповіді
        speak_and_send(response, message)

        os.remove(ogg_path)
        os.remove(wav_path)
    except Exception as e:
        bot.reply_to(message, f"🚨 Помилка голосового аналізатора: {e}")


# --- СИНТЕЗ МОВЛЕННЯ (TEXT-TO-SPEECH) ---
def speak_and_send(text, message):
    """Генерую голос та відправляю аудіо-відповідь."""
    tts = gTTS(text=text, lang='uk')
    voice_file = "jarvis_voice.mp3" # Змінено назву файлу
    tts.save(voice_file)

    # 1. Відправляємо в Telegram (щоб було чутно на телефоні або в навушниках телефону)
    with open(voice_file, 'rb') as voice:
        bot.send_voice(message.chat.id, voice)

    # 2. Відтворюємо локально на LOSTVAYNE-LOQ (для навушників ПК або динаміків)
    try:
        pygame.mixer.quit() # Скидаємо старе, якщо було
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048) # Нові параметри (buffer=2048)
        
        pygame.mixer.music.load(voice_file)
        pygame.mixer.music.play()
        
        # Чекаємо, поки договорить
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()
    except Exception as e:
        print(f"--- [LOG] Помилка звуку на LOSTVAYNE-LOQ: {e} ---") # Оновлене повідомлення про помилку

    # 3. Очищуємо тимчасовий файл
    if os.path.exists(voice_file):
        os.remove(voice_file)


# --- СИСТЕМНЕ КЕРУВАННЯ ---

@bot.message_handler(commands=['volup'], func=is_owner)
def volume_up(message):
    for _ in range(5): pyautogui.press('volumeup')
    bot.reply_to(message, "🔊 Гучність збільшено.")


@bot.message_handler(commands=['voldown'], func=is_owner)
def volume_down(message):
    for _ in range(5): pyautogui.press('volumedown')
    bot.reply_to(message, "🔉 Гучність зменшено.")


@bot.message_handler(commands=['deepclean'], func=is_owner)
def deep_clean(message):
    current_pid = os.getpid()
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        if 'python' in proc.info['name'].lower() and proc.info['pid'] != current_pid:
            try:
                proc.terminate()
                count += 1
            except:
                pass
    gc.collect()
    bot.reply_to(message, f"🧹 **Deep Clean завершено!**\nЗавершено фантомних процесів: {count}")


@bot.message_handler(commands=['shutdown'], func=is_owner)
def system_shutdown(message):
    if sys.platform == "win32":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("ТАК", callback_data="confirm_sd"),
                   telebot.types.InlineKeyboardButton("НІ", callback_data="cancel_sd"))
        bot.send_message(message.chat.id, "🚨 Ви впевнені, що хочете ВИМКНУТИ ПК?", reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ Доступно тільки для Windows.")


@bot.callback_query_handler(func=lambda call: call.data in ["confirm_sd", "cancel_sd"])
def handle_sd_confirm(call):
    if call.data == "confirm_sd" and sys.platform == "win32":
        bot.edit_message_text("☢️ Вимикаю систему...", call.message.chat.id, call.message.message_id)
        os.system("shutdown /s /t 1")
    else:
        bot.edit_message_text("✅ Скасовано.", call.message.chat.id, call.message.message_id)


@bot.message_handler(
    func=lambda m: is_owner(m) and m.text in ['📊 СТАТУС', '📸 СКРІНШОТ', '🔊 ГУЧНІСТЬ +', '🔉 ГУЧНІСТЬ -', '🌤️ ПОГОДА',
                                              '🧹 DEEP CLEAN'])
def handle_kb(message):
    if 'СТАТУС' in message.text:
        status(message)
    elif 'СКРІНШОТ' in message.text:
        take_screenshot(message)
    elif 'ПОГОДА' in message.text:
        get_weather(message)
    elif 'DEEP CLEAN' in message.text:
        deep_clean(message)
    elif '+' in message.text:
        volume_up(message)
    elif '-' in message.text:
        volume_down(message)


def take_screenshot(message):
    path = "screen.png"
    pyautogui.screenshot().save(path)
    with open(path, 'rb') as f: bot.send_photo(message.chat.id, f)
    os.remove(path)


@bot.message_handler(content_types=['text', 'photo', 'voice'], func=is_owner)
def chat(message):
    user_text = message.text or message.caption or "Проаналізуй це зображення."
    if user_text.lower().startswith("запам'ятай, що"):
        save_to_brain(get_current_timestamp(), user_text.replace("запам'ятай, що", "").strip())
        bot.reply_to(message, "✅ Збережено в локальний архів.")
        return

    image = None
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        image = Image.open(io.BytesIO(bot.download_file(file_info.file_path)))

    response_text = get_ai_response(user_text, image)
    bot.reply_to(message, response_text)
    speak_and_send(response_text, message)
    gc.collect()


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    clear_console()
    set_main_menu(bot)
    try:
        # 1. Спробуємо видалити старе з'єднання
        bot.remove_webhook()
        time.sleep(1) # Дамо серверу 1 секунду на роздуми
        
        print("--- [LOG] JARVIS MARK-4.0 VOICE OPERATIONAL ---")
        
        # 2. Запуск з ігноруванням старих повідомлень
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        
    except Exception as e:
        print(f"--- [CRITICAL ERROR] Помилка запуску: {e} ---")