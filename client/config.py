<<<<<<< HEAD
=======
import wget
from os import path
>>>>>>> 760cabc414e30a1821c8f5f8b022f841a234de1a
__test = False
def test():
    return __test
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