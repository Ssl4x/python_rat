"""
Консольный интерфейс для управления системкой
"""

import warnings
warnings.filterwarnings("ignore")

import threading
import os
from time import sleep

from server import ManyServers, help_command, Notificator
import config as config
import asyncio

import logging

logging.basicConfig(level=logging.INFO)

class ConsoleNotificator:
    """Класс для передачи уведомлений из клиента в консоль сервера"""
    def make_notification(text: str, *args):
        print(text)


class ConsoleController:
    def __init__(self):
        pass

    def command_dispatcher(command: str):
        pass
    
    @staticmethod
    def clients():
        return(mult.view_all_servers())
    
    @staticmethod
    def help():
        return(help_command())
    
    def client()