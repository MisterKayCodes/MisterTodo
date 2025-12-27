from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from bot.keyboards.reply import main_menu_kb, BTN_NEW_TASK, BTN_MY_LIST
from bot.handlers.states import TaskCreation  # Ensure TaskCreation has a 'priority' state

# Rule 11: Only import the Manager, not the Repo
from services.task_manager import TaskManager
from services.stats import HabitStats

router = Router()
task_manager = TaskManager()  # Use the manager, not the repo (Rule 3)

# --- Keyboards ---

def build_task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Done", callback_data=f"done:{task_id}"),
            InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete:{task_id}")
        ]
    ])

def build_priority_kb() -> InlineKeyboardMarkup:
    """Rule 6: Explicit priority selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Low", callback_data="prio:Low"),
            InlineKeyboardButton(text="🟡 Medium", callback_data="prio:Medium"),
            InlineKeyboardButton(text="🔴 High", callback_data="prio:High")
        ]
    ])

# --- Handlers ---

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome to {hbold('Mister Todo')}!\n\nUse the buttons below to manage your tasks.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Habit Stats") # Assuming this BTN exists in your main_menu_kb
@router.message(Command("habitstats"))
async def cmd_habitstats(message: Message):
    """Phase 3: The Habit Stats Summary UI."""
    stats = HabitStats(user_id=message.from_user.id, task_manager=task_manager)
    
    streak = stats.get_current_streak()
    progress = stats.get_progress_stats()
    
    # Rule 8: Visual Progress Bar (Boring but effective)
    filled = int(progress['percent'] * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)

    response = (
        f"📊 {hbold('Your Productivity Stats')}\n\n"
        f"🔥 Streak: {hbold(f'{streak} days')}\n"
        f"🎯 Goal: {progress['count']}/{progress['goal']}\n"
        f"Lvl: [{bar}] {int(progress['percent']*100)}%\n\n"
        f"{'🌟 Goal Achieved!' if progress['is_goal_reached'] else 'Keep pushing! 🚀'}"
    )
    await message.answer(response, parse_mode="HTML")

@router.message(F.text == BTN_MY_LIST)
@router.message(Command("list"))
async def cmd_list(message: Message):
    # Rule 11: Using TaskManager returns a list of Task objects
    tasks = task_manager.get_tasks(user_id=message.from_user.id)

    if not tasks:
        await message.answer("📋 Your list is empty.", reply_markup=main_menu_kb())
        return

    for task in tasks:
        # Now we can use task.priority and task.name safely
        prio_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.priority, "⚪")
        text = (
            f"{prio_emoji} {hbold(task.name)}\n"
            f"📝 {hitalic(task.description or 'No description')}\n"
            f"⏰ Due: {task.due_date}"
        )
        await message.answer(text, reply_markup=build_task_inline_kb(task.id), parse_mode="HTML")

# --- Task Creation FSM with Priority ---

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
    await message.answer("📅 Enter due date (or /skip):")

@router.message(TaskCreation.due_date)
async def process_due_date(message: Message, state: FSMContext):
    due = message.text if message.text != "/skip" else "No deadline"
    await state.update_data(due_date=due)
    
    # NEW STEP: Rule 6 - Explicit Priority Selection
    await state.set_state(TaskCreation.priority)
    await message.answer("⚖️ Select Task Priority:", reply_markup=build_priority_kb())

@router.callback_query(TaskCreation.priority, F.data.startswith("prio:"))
async def process_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split(":")[1]
    data = await state.get_data()
    
    # Finalize creation via Manager
    task_manager.add_task(
        user_id=callback.from_user.id,
        name=data['name'],
        description=data['description'],
        due_date=data['due_date'],
        priority=priority
    )
    
    await callback.message.edit_text(f"✅ Task {hbold(data['name'])} created with {priority} priority!")
    await callback.message.answer("What's next?", reply_markup=main_menu_kb())
    await state.clear()
