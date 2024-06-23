@echo off

python.exe -m pip install --upgrade pi
pip install dearpygui discord psutil requests discord_webhook
python gui_builder.py
