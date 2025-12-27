from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

# Rule 3: Separation of UI Components
from bot.keyboards.reply import main_menu_kb, BTN_NEW_TASK, BTN_MY_LIST, BTN_STATS, BTN_ARCHIVE
from bot.keyboards.inline import task_inline_kb, build_priority_kb, build_archive_kb
from bot.handlers.states import TaskCreation
from bot.utils import normalize_date 

from services.task_manager import TaskManager
from services.stats import HabitStats

router = Router()
task_manager = TaskManager()

# --- Navigation Handlers ---

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Rule 1: Bootstrapping user into a known system state."""
    await message.answer(
        f"Welcome to {hbold('Mister Todo')}!\n\nUse the buttons below to manage your tasks.",
        reply_markup=main_menu_kb()
    )

@router.message(F.text == BTN_STATS)
@router.message(Command("habitstats"))
async def cmd_habitstats(message: Message):
    """Phase 3: Productivity Logic & Metrics."""
    stats = HabitStats(user_id=message.from_user.id, task_manager=task_manager)
    streak = stats.get_current_streak()
    progress = stats.get_progress_stats()
    
    filled = int(progress['percent'] * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)

    response = (
        f"📊 {hbold('Your Productivity Stats')}\n\n"
        f"🔥 Streak: {hbold(f'{streak} days')}\n"
        f"🎯 Goal: {progress['count']}/{progress['goal']}\n"
        f"Lvl: [{bar}] {int(progress['percent']*100)}%\n\n"
        f"{'🌟 Goal Achieved!' if progress['is_goal_reached'] else 'Keep pushing! 🚀'}"
    )
    await message.answer(response)

@router.message(F.text == BTN_MY_LIST)
@router.message(Command("list"))
async def cmd_list(message: Message):
    """Rule 11: Displaying active durable state."""
    tasks = task_manager.get_tasks(user_id=message.from_user.id)
    if not tasks:
        await message.answer("📋 Your list is empty.", reply_markup=main_menu_kb())
        return

    for task in tasks:
        prio_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.priority, "⚪")
        text = (
            f"{prio_emoji} {hbold(task.name)}\n"
            f"📝 {hitalic(task.description or 'No description')}\n"
            f"⏰ Due: {task.due_date}"
        )
        # Using centralized inline builder
        await message.answer(text, reply_markup=task_inline_kb(task.id))

# --- Task Creation FSM ---

@router.message(F.text == BTN_NEW_TASK)
async def cmd_newtask(message: Message, state: FSMContext):
    await state.set_state(TaskCreation.name)
    await message.answer("📝 Enter task name:", reply_markup=ReplyKeyboardRemove())

@router.message(TaskCreation.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(TaskCreation.description)
    await message.answer("📝 Enter description (or /skip):")

@router.message(TaskCreation.description)
async def process_description(message: Message, state: FSMContext):
    desc = message.text if message.text != "/skip" else "No description"
    await state.update_data(description=desc)
    await state.set_state(TaskCreation.due_date)
    await message.answer("📅 When is this due? (e.g., 'tomorrow', '20th Dec', or /skip):")

@router.message(TaskCreation.due_date)
async def process_due_date(message: Message, state: FSMContext):
    """Rule 6: Normalizing user intent into predictable data."""
    raw_date = message.text.strip()
    clean_date = normalize_date(raw_date)
    
    await state.update_data(due_date=clean_date)
    await state.set_state(TaskCreation.priority)
    
    # Using centralized inline builder
    await message.answer(
        f"📅 Date interpreted as: {hbold(clean_date)}\n\n⚖️ Select Task Priority:", 
        reply_markup=build_priority_kb()
    )

# --- Archive Handler ---

@router.message(F.text == BTN_ARCHIVE)
@router.message(Command("archive"))
async def cmd_archive(message: Message):
    """Phase 4: Entry point for Historical Archive View."""
    user_id = message.from_user.id
    completed_tasks = task_manager.get_archive(user_id, page=0)

    if not completed_tasks:
        await message.answer("Your archive is empty. Finish some tasks first! 🚀")
        return

    has_more = len(completed_tasks) >= 10
    response = f"📜 {hbold('Completed Tasks Archive (P1)')}\n\n"
    for task in completed_tasks:
        done_date = task.completed_at[:10] if task.completed_at else "---"
        response += f"✅ {task.name} — {hitalic(done_date)}\n"

    # Using centralized inline builder
    await message.answer(response, reply_markup=build_archive_kb(0, has_more))
