@echo off
:: Налаштовую кодування для коректного відображення української мови
chcp 65001 > nul
set PYTHONPATH=.

echo [>] Ініціалізація LOSTVAYNE-CORE...
echo [>] Сер, запускаю ваш пульт керування JARVIS.

:: Запуск графічного інтерфейсу з віртуального середовища
".venv\Scripts\python.exe" dashboard/control_panel.py

if %errorlevel% neq 0 (
    echo [!] Виникла помилка при запуску. Перевірте консоль.
    pause
)