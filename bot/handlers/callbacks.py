from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

# Rule 11: Use Manager and Stats, not raw Repo
from services.task_manager import TaskManager
from services.stats import HabitStats

router = Router()
task_manager = TaskManager()

@router.callback_query(F.data.startswith("done:"))
async def callback_done_handler(callback: CallbackQuery):
    """Rule 1: Transitions task to completed state and triggers stats update."""
    try:
        task_id = int(callback.data.split(":")[1])
        user_id = callback.from_user.id

        success = task_manager.mark_task_done(task_id, user_id)

        if success:
            # Rule 10: Provide immediate feedback on the new state
            stats = HabitStats(user_id=user_id, task_manager=task_manager)
            progress = stats.get_progress_stats()
            
            msg = (
                f"✅ {hbold('Task Completed!')}\n"
                f"Daily Progress: {progress['count']}/{progress['goal']} "
                f"{'🎉' if progress['is_goal_reached'] else '🚀'}"
            )
            await callback.message.edit_text(msg, parse_mode="HTML")
            await callback.answer("Stats Updated!")
        else:
            await callback.answer("❌ Task not found or already done.", show_alert=True)
    except (ValueError, IndexError):
        await callback.answer("❗ Data Corruption Error", show_alert=True)

@router.callback_query(F.data.startswith("delete:"))
async def callback_delete_handler(callback: CallbackQuery):
    """Rule 5: Idempotent deletion handler."""
    try:
        task_id = int(callback.data.split(":")[1])
        user_id = callback.from_user.id

        if task_manager.delete_task(task_id, user_id):
            await callback.message.delete()
            await callback.answer("🗑 Task removed.")
        else:
            await callback.answer("❌ Task not found.", show_alert=True)
    except Exception:
        await callback.answer("❗ Error during deletion.", show_alert=True)

# Love From Mister
