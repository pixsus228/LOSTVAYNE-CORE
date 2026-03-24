from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv, set_key

# шлях до файлу з ключем шифрування (не плутати з сесією!)
KEY_FILE = "engine/data/secret.key"


def generate_key():
    # створив унікальний ключ шифрування, якщо його ще немає
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("[GHOST] Сгенеровано новий ключ шифрування.")


def get_cipher():
    with open(KEY_FILE, "rb") as f:
        return Fernet(f.read())


def encrypt_data(data):
    # зашифрував ваші дані перед записом у .env
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data):
    # розшифрував дані для використання в Selenium
    cipher = get_cipher()
    return cipher.decrypt(encrypted_data.encode()).decode()


if __name__ == "__main__":
    generate_key()
    # Сер, введіть свій сесійний ключ тут один раз для шифрування
    raw_key = input("Введіть JR_SESSION_KEY для шифрування: ")
    encrypted = encrypt_data(raw_key)

    # записую зашифрований ключ у .env
    set_key(".env", "JR_SESSION_KEY_ENCRYPTED", encrypted)
    print("[GHOST] Сер, ваші дані зашифровані та збережені в .env.")