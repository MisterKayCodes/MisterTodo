import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import BOT_TOKEN


async def start_handler(message: Message):
    await message.answer("✅ Mister Todo Bot is alive!")


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# Love From Mister
