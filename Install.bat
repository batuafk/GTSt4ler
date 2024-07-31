@echo off

python.exe -m pip install --upgrade pip
pip install pyinstaller dearpygui discord psutil requests discord_webhook
python gui_builder.py
