from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from bot.keyboards.reply import main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu_kb()
    await message.answer(
        "Mister Todo Bot is live!\n\nWelcome! Use the buttons below to get started.",
        reply_markup=keyboard
    )

@router.message(F.text)
async def fallback_message(message: Message):
    # Explicitly handle only text messages that are not commands,
    # since commands are routed before this handler.
    keyboard = main_menu_kb()
    await message.answer(
        "I didn't quite catch that. Please use the buttons below to navigate.",
        reply_markup=keyboard
    )

# Love From Mister
