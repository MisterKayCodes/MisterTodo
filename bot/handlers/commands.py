from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from bot.keyboards.reply import main_menu_kb, BTN_NEW_TASK, BTN_MY_LIST
from bot.handlers.states import TaskCreation
from services.persistence import TaskRepository

router = Router()
task_repo = TaskRepository() # Rule 11: Persistent instance

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu_kb()
    await message.answer(
        f"Welcome to {hbold('Mister Todo')}!\n\nUse the buttons below to manage your tasks.",
        reply_markup=keyboard,
        parse_mode="HTML" # Rule 13: Consistent HTML parsing
    )

@router.message(F.text == BTN_NEW_TASK)
@router.message(Command("newtask"))
async def cmd_newtask(message: Message, state: FSMContext):
    await state.set_state(TaskCreation.name)
    await message.answer(
        "📝 Please enter the name of your new task:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text == BTN_MY_LIST)
@router.message(Command("list"))
async def cmd_list(message: Message):
    """Rule 4: Fetches and lists user tasks (Durable Retrieval)."""
    tasks = task_repo.get_tasks(user_id=message.from_user.id)
    
    if not tasks:
        await message.answer(
            f"📋 Your task list is empty. Use {hbold(BTN_NEW_TASK)} to start.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return
    
    task_lines = []
    for task in tasks:
        # Rule 12: Safe formatting for output
        task_lines.append(
            f"🆔 {task['id']} - {hbold(task['name'])}\n"
            f"📝 {hitalic(task['description'])}\n"
            f"⏰ Due: {task['due_date']}\n"
            f"----------------------------------"
        )
    
    await message.answer(
        f"📋 {hbold('Your Tasks:')}\n\n" + "\n".join(task_lines),
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )

# ---------- FSM Flow (Rule 1) ----------

@router.message(TaskCreation.name)
async def process_task_name(message: Message, state: FSMContext):
    task_name = message.text.strip()
    if not task_name:
        await message.answer("❗ Task name cannot be empty:")
        return

    await state.update_data(name=task_name)
    await state.set_state(TaskCreation.description)
    await message.answer(
        f"✅ Name saved: {hbold(task_name)}\n\nNow, enter a description (or /skip):",
        parse_mode="HTML"
    )

@router.message(TaskCreation.description, Command("skip"))
@router.message(TaskCreation.description)
async def process_task_desc(message: Message, state: FSMContext):
    if (message.text and message.text.startswith('/skip')) or message.text.lower() == "none":
        description = "No description provided."
    else:
        description = message.text.strip()
    
    await state.update_data(description=description)
    await state.set_state(TaskCreation.due_date)
    await message.answer("📅 When is this due?\n(Type a date or /skip for 'No deadline'):")

@router.message(TaskCreation.due_date, Command("skip"))
@router.message(TaskCreation.due_date)
async def process_task_due_date(message: Message, state: FSMContext):
    if (message.text and message.text.startswith('/skip')) or message.text.lower() == "none":
        due_date = "No deadline"
    else:
        due_date = message.text.strip()
    
    user_data = await state.get_data()

    # Rule 2: Save to Durable Storage
    task_repo.add_task(
        user_id=message.from_user.id,
        name=user_data['name'],
        description=user_data['description'],
        due_date=due_date
    )

    response = (
        f"🎯 {hbold('Task Created Successfully!')}\n\n"
        f"📌 {hbold(user_data['name'])}\n"
        f"📝 {hitalic(user_data['description'])}\n"
        f"⏰ Due: {due_date}"
    )
    
    await message.answer(response, parse_mode="HTML", reply_markup=main_menu_kb())
    await state.clear()

# ---------- Fallback (ALWAYS LAST) ----------

@router.message(F.text)
async def fallback_message(message: Message):
    await message.answer(
        "I didn't quite catch that. Please use the buttons below to navigate.",
        reply_markup=main_menu_kb()
    )

# Love From Mister
