__test = False
if not __test:
    import sys
    sys.path.append("/usr/local/lib/python3.6/dist-packages/")
    sys.path.append("/usr/local/lib/python3.6/")
SERVER_IP = "127.0.0.1" if __test else "185.173.93.219"
SERVER_PORT = 8080 if __test else 9090
NOTI_IDS = [1350534067]
TELEGRAM_TOKEN = "5241143500:AAFshCNQ2oKRipPFoOK434WScUkflKyK5L8"