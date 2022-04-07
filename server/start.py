"""
Телеграм интерфейс для управления системкой
"""

import os
from server import ManyServers
import config as config
import asyncio

import logging


from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = config.TELEGRAM_TOKEN

mult = ManyServers()
asyncio.run(mult.add_connection())

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
    res = mult.make_command_to_server(message.text)
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