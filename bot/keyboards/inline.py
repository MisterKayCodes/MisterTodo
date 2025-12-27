from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    """Standard buttons for active tasks."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Done", callback_data=f"done:{task_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete:{task_id}")
            ]
        ]
    )

def build_priority_kb() -> InlineKeyboardMarkup:
    """Rule 6: Explicit priority selection during task creation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢 Low", callback_data="prio:Low"),
                InlineKeyboardButton(text="🟡 Medium", callback_data="prio:Medium"),
                InlineKeyboardButton(text="🔴 High", callback_data="prio:High")
            ]
        ]
    )

def build_archive_kb(page: int, has_more: bool) -> InlineKeyboardMarkup:
    """
    Phase 4: Navigation and Classification logic for the Archive.
    Separates pagination from sorting filters.
    """
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"archive:{page-1}"))
    if has_more:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"archive:{page+1}"))
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_buttons,  # Row 1: Pagination
            [             # Row 2: Time Classification (Rule 11)
                InlineKeyboardButton(text="📅 Today", callback_data="sort:today"),
                InlineKeyboardButton(text="📅 Week", callback_data="sort:weekly"),
                InlineKeyboardButton(text="📅 Month", callback_data="sort:monthly")
            ],
            [             # Row 3: Data Export (Rule 2)
                InlineKeyboardButton(text="📊 Export CSV", callback_data="export_csv")
            ]
        ]
    )

# Love From Mister
