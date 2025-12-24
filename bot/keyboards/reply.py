from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_NEW_TASK = "➕ New Task"
BTN_MY_LIST = "📋 My List"
BTN_STATS = "📊 Habit Stats"
BTN_TIMER = "⏱️ Active Timer"

def main_menu_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_NEW_TASK), KeyboardButton(text=BTN_MY_LIST)],
            [KeyboardButton(text=BTN_STATS), KeyboardButton(text=BTN_TIMER)]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Choose an option..."
    )
    return keyboard

# Love From Mister
