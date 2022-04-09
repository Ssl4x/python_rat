import os
import wget


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

