from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from bot.keyboards.inline import task_inline_kb
from services.persistence import TaskRepository

router = Router()
task_repo = TaskRepository()


@router.callback_query(lambda c: c.data and c.data.startswith("done:"))
async def callback_done_handler(callback: CallbackQuery):
    # Extract task_id from callback data
    task_id_str = callback.data.split(":")[1]
    if not task_id_str.isdigit():
        await callback.answer("Invalid task ID.", show_alert=True)
        return

    task_id = int(task_id_str)
    user_id = callback.from_user.id

    success = task_repo.mark_task_done(task_id, user_id)

    if success:
        await callback.answer("✅ Task marked as done!")
        # Optionally edit the message to show the task is done or remove buttons
        await callback.message.edit_reply_markup(None)
    else:
        await callback.answer("❌ Task not found or already done.", show_alert=True)


@router.callback_query(lambda c: c.data and c.data.startswith("delete:"))
async def callback_delete_handler(callback: CallbackQuery):
    # Extract task_id from callback data
    task_id_str = callback.data.split(":")[1]
    if not task_id_str.isdigit():
        await callback.answer("Invalid task ID.", show_alert=True)
        return

    task_id = int(task_id_str)
    user_id = callback.from_user.id

    success = task_repo.delete_task(task_id, user_id)

    if success:
        await callback.answer("🗑 Task deleted!")
        # Optionally delete the message or update markup
        await callback.message.delete()
    else:
        await callback.answer("❌ Task not found or could not be deleted.", show_alert=True)

# Love From Mister