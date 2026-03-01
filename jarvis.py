import warnings
import io
from PIL import Image

# Пригнічую всі попередження про застарілі пакети, щоб консоль мого LOQ залишалася чистою
warnings.filterwarnings("ignore")

import telebot
import psutil
import platform
import google.generativeai as genai
import config  # Використовую власні ключі доступу з конфіденційного файлу

# Ініціалізую Telegram-бота, звертаючись до токена в моєму Секторі Безпеки
bot = telebot.TeleBot(config.BOT_TOKEN)

# Налаштовую зв'язок із ШІ через REST-транспорт для стабільності каналу
# Використовую стабільну версію API v1 без префікса v1beta
genai.configure(api_key=config.GEMINI_KEY)
print(f"--- [LOG] GenAI Library Version: {genai.__version__} ---")

# Сканую доступні моделі для перевірки прав доступу (Діагностика)
print("--- [DIAGNOSTIC] Scanning Available Models... ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Found: {m.name}")

# Визначаю системні налаштування глобально: фокусуюся на авто, техніці та безпеці
SYSTEM_PROMPT = (
    "Ти — Джарвіс, особистий ШІ Агента Алекса. "
    "Алекс — власник Lenovo LOQ, водій ВАЗ-2111. "
    "Твій стиль: професійний, відданий. Відповідай українською. "
    "Ігноруй будь-які запити про навчальні заклади чи агроінженерію."
)

# --- Security: Access Control ---
def is_owner(message):
    return message.from_user.id == config.OWNER_ID

# Ініціалізую основне ядро та сесію чату глобально (Пам'ять)
# Використовую gemini-1.5-flash як основну стабільну модель (2.0 поки що нестабільна)
main_model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=SYSTEM_PROMPT)
chat_session = main_model.start_chat(history=[])

def get_ai_response(user_text, image=None):
    """Використовую цей блок для зв'язку з обраним нейронним ядром."""
    try:
        # Відправляю повідомлення в існуючу сесію (зберігає контекст)
        log_msg = f"Текст: {user_text[:50]}..."
        if image:
            log_msg += " [📸 ФОТО]"
        print(f"--- [LOG] Надсилаю запит до Gemini 1.5 Flash ({genai.__version__}): {log_msg} ---")
        
        # Додаю префікс для стилю, але в історії це збережеться
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


@bot.message_handler(commands=['start'], func=is_owner)
def welcome(message):
    # Вітаю оператора та підтверджую активацію систем версії 2026 року
    bot.reply_to(message, "Системи активовані. Джарвіс онлайн на базі Gemini 2.0. 🛡️")


@bot.message_handler(commands=['status'], func=is_owner)
def status(message):
    """Проводжу повну діагностику ресурсів мого Lenovo LOQ."""
    # Зчитую поточні показники навантаження CPU та RAM
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    # Відправляю звіт про стан заліза прямо в командний центр Telegram
    bot.reply_to(message,
                     f"--- ДІАГНОСТИКА S.H.I.E.L.D. ---\n🖥️ Хост: {platform.node()}\n⚙️ CPU: {cpu}%\n📊 RAM: {ram}%\n🟢 Ядро: Gemini Flash Latest")

@bot.message_handler(commands=['reset'], func=is_owner)
def reset_memory(message):
    """Очищення буфера пам'яті нейромережі."""
    global chat_session
    # Перезапускаю сесію з порожньою історією
    chat_session = main_model.start_chat(history=[])
    bot.reply_to(message, "🧠 Пам'ять очищено. Протокол 'Tabula Rasa' виконано. Готовий до нових завдань.")

# Обробник для неавторизованих користувачів
@bot.message_handler(func=lambda message: not is_owner(message))
def unauthorized_access(message):
    bot.reply_to(message, "Доступ заборонено. Ви не Агент Алекс.")

@bot.message_handler(content_types=['text', 'photo'], func=is_owner)
def chat(message):
    """Обробляю текстові запити Агента Алекса через термінал."""
    # Встановлюю правильний синтаксис для статусу друку через знак '='
    bot.send_chat_action(message.chat.id, action='typing')
    
    # Якщо тексту немає (наприклад, просто фото), встановлюю дефолтний запит
    user_text = message.text if message.text else None
    # Якщо фото є у повідомленні (воно приходить як caption, якщо є підпис)
    if message.caption:
        user_text = message.caption
    
    if user_text is None and message.photo:
        user_text = "Що зображено на цьому фото?"

    image = None
    if message.photo:
        # Отримуємо файл з найбільшою роздільною здатністю (останній у списку)
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Конвертуємо байти в об'єкт зображення
        image = Image.open(io.BytesIO(downloaded_file))

    # Отримую відповідь від ШІ (передаю текст і фото, якщо є)
    reply = get_ai_response(user_text, image)
    bot.reply_to(message, reply)


if __name__ == "__main__":
    # Запускаю постійний моніторинг вхідних запитів та виводжу статус у консоль PyCharm
    print(f"--- [LOG] JARVIS_LOQ_TERMINAL IS FULLY OPERATIONAL ---")
    bot.infinity_polling()