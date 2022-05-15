__test = False
def test():
    return __test
SERVER_IP = "127.0.0.1" if __test else "185.173.93.219"
SERVER_PORT = 8080 if __test else 9090