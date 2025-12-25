from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Done", callback_data=f"done:{task_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete:{task_id}")
            ]
        ]
    )
# Love From Mister