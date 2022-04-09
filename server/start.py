"""
Телеграм интерфейс для управления системкой
"""

import threading
import os
from server import ManyServers
import config as config
import asyncio
from multiprocessing import Process

import logging


from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = config.TELEGRAM_TOKEN

mult = ManyServers()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['servers'])
async def view_all_servers(message: types.Message):
    await message.reply(mult.view_all_servers())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Интерфейс для управления системкой")

@dp.message_handler()
async def echo(message: types.Message):
    res = await mult.make_command_to_server(message.text)
    if type(res) != str:
        await message.answer_document(open("screen.png", "rb"))
        os.remove("screen.png")
    else:
        await message.answer(res)

def connection_monitor():
    # p = Process(target=mult.add_connection)
    # p.start()
    t = threading.Thread(target=(mult.add_connection), daemon=True)
    t.start()

if __name__ == '__main__':
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