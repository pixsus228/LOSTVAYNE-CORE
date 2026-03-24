@echo off
chcp 65001 > nul
set PYTHONPATH=.
echo [>] Сер, LOSTVAYNE-CORE активується...
python dashboard/control_panel.py
pause