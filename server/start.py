"""
Телеграм интерфейс для управления системкой
"""

import os
from server import Server
import config as config

import logging


from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = config.TELEGRAM_TOKEN

active_server = Server(config.SERVER_IP, config.SERVER_PORT)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Интерфейс для управления системкой")

@dp.message_handler()
async def echo(message: types.Message):
    res = active_server.step(message.text)
    if type(res) != str:
        await message.answer_document(open("screen.png", "rb"))
        os.remove("screen.png")
    else:
        await message.answer(res)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as er:
        print(er)
        input()