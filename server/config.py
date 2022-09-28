import wget
from os import path
__test = False
if not __test:
    import sys
    sys.path.append("/usr/local/lib/python3.6/dist-packages/")
    sys.path.append("/usr/local/lib/python3.6/")
def get_config_from_drive() -> None:
    wget.download("https://drive.google.com/uc?export=download&confirm=no_antivirus&id=14ERAUwoo4XpkW7lvuwHM0e-G4PVfzODY", "config.cfg")
def parse_config() -> dict:
    # Проверка наличия конфига, при отсутствии - подгрузка
    if not path.exists("./config.cfg"):
        get_config_from_drive()
    with open("config.cfg", "r") as cfg:
        # host ip
        server_ip = cfg.readline()
    return {"ip": server_ip}
params = parse_config()
SERVER_IP = "127.0.0.1" if __test else params["ip"]
SERVER_PORT = 8080 if __test else 9090
NOTI_IDS = [1350534067]
TELEGRAM_TOKEN = "5241143500:AAHZ1_ErOMGdrfdm3DSSW3Tn9FpFsxK4Ags"