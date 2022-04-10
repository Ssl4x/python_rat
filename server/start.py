"""
Телеграм интерфейс для управления системкой
"""

import threading
import os
from server import ManyServers
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
    await message.reply(mult.view_all_servers())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """обработка команд start и help"""
    await message.reply("Интерфейс для управления системкой")

@dp.message_handler(commands=['client'])
async def client(message: types.Message):
    """Создание запроса к клиенту"""
    res = await mult.make_command_to_server(message.text)
    if res is None:
        await message.answer("Nothing")
    if type(res) != str:
        if res[0] == "screen":
            await message.answer_document(open("screen.png", "rb"))
            os.remove("screen.png")
        else:
            for i in res[1:]:
                await message.answer(i)        
    else:
        await message.answer(res)

@dp.message_handler(content_types="photo")
async def client(message:types.Message):
    await message.reply_photo(message.photo[-1].file_id)

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
