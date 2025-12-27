import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

# Rule 3: Centralized UI and Logic Imports
from bot.keyboards.inline import build_archive_kb
from bot.keyboards.reply import main_menu_kb
from services.task_manager import TaskManager
from services.stats import HabitStats

router = Router()
task_manager = TaskManager()

# --- Task Interaction Handlers ---

@router.callback_query(F.data.startswith("done:"))
async def callback_done_handler(callback: CallbackQuery):
    """Rule 1: Transitions task to completed state and updates stats."""
    try:
        task_id = int(callback.data.split(":")[1])
        success = task_manager.mark_task_done(task_id, callback.from_user.id)

        if success:
            stats = HabitStats(user_id=callback.from_user.id, task_manager=task_manager)
            progress = stats.get_progress_stats()
            
            msg = (
                f"✅ {hbold('Task Completed!')}\n"
                f"Daily Progress: {progress['count']}/{progress['goal']} "
                f"{'🎉' if progress['is_goal_reached'] else '🚀'}"
            )
            await callback.message.edit_text(msg)
        else:
            await callback.answer("❌ Task not found or already done.", show_alert=True)
    except Exception:
        await callback.answer("❗ Data Error", show_alert=True)

@router.callback_query(F.data.startswith("prio:"))
async def process_priority_callback(callback: CallbackQuery, state: FSMContext):
    """Rule 6: Finalizes task creation based on explicit priority selection."""
    priority = callback.data.split(":")[1]
    data = await state.get_data()
    
    task_manager.add_task(
        user_id=callback.from_user.id,
        name=data['name'],
        description=data.get('description'),
        due_date=data.get('due_date'),
        priority=priority
    )
    
    await callback.message.edit_text(f"✅ Task {hbold(data['name'])} created!")
    await callback.message.answer("What's next?", reply_markup=main_menu_kb())
    await state.clear()

# --- Archive & Classification Handlers ---

@router.callback_query(F.data.startswith("archive:"))
async def handle_archive_pagination(callback: CallbackQuery):
    """Phase 4: Historical state navigation."""
    page = int(callback.data.split(":")[1])
    tasks = task_manager.get_archive(callback.from_user.id, page=page)
    
    has_more = len(tasks) >= 10
    text = f"📜 {hbold(f'Archive (Page {page + 1})')}\n\n"
    for t in tasks:
        date = t.completed_at[:10] if t.completed_at else "---"
        text += f"✅ {t.name} — {hitalic(date)}\n"

    await callback.message.edit_text(text, reply_markup=build_archive_kb(page, has_more))
    await callback.answer()

@router.callback_query(F.data.startswith("sort:"))
async def handle_archive_sorting(callback: CallbackQuery):
    """Rule 10: Classify tasks by Daily, Weekly, or Monthly periods."""
    period = callback.data.split(":")[1]
    tasks = task_manager.get_tasks_by_period(callback.from_user.id, period)
    
    if not tasks:
        await callback.answer(f"No tasks found for this period: {period}.", show_alert=True)
        return

    text = f"📊 {hbold(f'Tasks: {period.capitalize()}')}\n\n"
    for t in tasks:
        day = t.completed_at[:10] if t.completed_at else "---"
        text += f"🗓 {hitalic(day)} | {t.name}\n"
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 Back to Archive", callback_data="archive:0")
    ]])
    
    await callback.message.edit_text(text, reply_markup=back_kb)
    await callback.answer()

@router.callback_query(F.data == "export_csv")
async def handle_csv_export(callback: CallbackQuery):
    """Rule 18: Safe delivery of the grouped task report."""
    user_id = callback.from_user.id
    file_path = task_manager.export_tasks_to_csv(user_id)
    
    if os.path.exists(file_path):
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption=f"📊 {hbold('Mister_Todo Export')}\nTasks grouped by completion date."
        )
        await callback.answer("Report sent!")
    else:
        await callback.answer("❌ Export failed: No file generated.", show_alert=True)

# Love From Mister
