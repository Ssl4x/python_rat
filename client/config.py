import wget
from os import path
__test = True
def test():
    return __test
def get_config_from_drive() -> None:
    wget.download("https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1LZ8xi_5vIFeNO1FquiD87XVLyc2K3tI89lLhqeUI408", "config.cfg")
def parse_config() -> dict:
    # Проверка наличия конфига, при отсутствии - подгрузка
    if not path.exists("./config.cfg"):
        get_config_from_drive()
    with open("config.cfg", "r") as cfg:
        # host ip
        server_ip = cfg.readline()
    return {"ip": server_ip}
params = parse_config
SERVER_IP = "127.0.0.1" if __test else params["ip"]
SERVER_PORT = 8080 if __test else 9090