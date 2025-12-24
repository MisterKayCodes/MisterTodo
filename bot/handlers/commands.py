from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from bot.keyboards.reply import main_menu_kb, BTN_NEW_TASK, BTN_MY_LIST
from bot.handlers.states import TaskCreation

router = Router()

# ---------- General Handlers ----------

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu_kb()
    await message.answer(
        f"Welcome to {hbold('Mister Todo')}!\n\nUse the buttons below to manage your tasks.",
        reply_markup=keyboard,
        parse_mode="HTML"
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
    """Rule 4: Moved above fallback so it actually triggers."""
    await message.answer(
        f"{hbold('📋 Your Tasks')}\n\nYour list is currently empty. Use the {hbold(BTN_NEW_TASK)} button to add one!",
        parse_mode="HTML"
    )

# ---------- FSM Flow Handlers (Rule 1) ----------

@router.message(TaskCreation.name)
async def process_task_name(message: Message, state: FSMContext):
    task_name = message.text.strip()
    if not task_name:
        await message.answer("❗ Task name cannot be empty. Please enter a valid name:")
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
    
    response = (
        f"🎯 {hbold('Task Created Successfully!')}\n\n"
        f"📌 {hbold(user_data['name'])}\n"
        f"📝 {hitalic(user_data['description'])}\n"
        f"⏰ Due: {due_date}"
    )
    
    await message.answer(response, parse_mode="HTML", reply_markup=main_menu_kb())
    await state.clear()

# ---------- Fallback Handler (Rule 4: ALWAYS LAST) ----------

@router.message(F.text)
async def fallback_message(message: Message):
    keyboard = main_menu_kb()
    await message.answer(
        "I didn't quite catch that. Please use the buttons below to navigate.",
        reply_markup=keyboard
    )

# Love From Mister
