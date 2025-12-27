from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Rule 13: Consistent naming and explicit constants
BTN_NEW_TASK = "➕ New Task"
BTN_MY_LIST = "📋 My List"
BTN_STATS = "📊 Habit Stats"
BTN_ARCHIVE = "📜 View Archive"  # UPDATED from BTN_TIMER

def main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Rule 3: Single Responsibility - Provides the main navigation state.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            # Row 1: Primary Actions
            [KeyboardButton(text=BTN_NEW_TASK), KeyboardButton(text=BTN_MY_LIST)],
            # Row 2: Insights & History
            [KeyboardButton(text=BTN_STATS), KeyboardButton(text=BTN_ARCHIVE)]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Choose an option..."
    )
    return keyboard

# Love From Mister
