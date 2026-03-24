@echo off
chcp 65001 > nul
title LOSTVAYNE CORE v2.3
color 0C

cd /d "C:\Users\Loq\PycharmProjects\Jarvis_LOQ_Terminal"

if not exist .venv (
    echo [!] СЕР, ВІРТУАЛЬНЕ СЕРЕДОВИЩЕ НЕ ЗНАЙДЕНО.
    pause
    exit
)

call .venv\Scripts\activate
echo [>] СИСТЕМА LOSTVAYNE CORE АКТИВОВАНА.
echo [>] СТАТУС: ОНЛАЙН.

python dashboard/control_panel.py
pause