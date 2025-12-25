from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters.command import Command, CommandObject
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hitalic

from bot.keyboards.reply import main_menu_kb, BTN_NEW_TASK, BTN_MY_LIST
from bot.handlers.states import TaskCreation
from services.persistence import TaskRepository

router = Router()
task_repo = TaskRepository()  # Persistent DB instance

# Helper to build inline keyboard for a task
def build_task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Done", callback_data=f"done:{task_id}"),
            InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete:{task_id}")
        ]
    ])

# /start command with main menu
@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu_kb()
    await message.answer(
        f"Welcome to {hbold('Mister Todo')}!\n\nUse the buttons below to manage your tasks.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# /newtask or BTN_NEW_TASK - start FSM for task creation
@router.message(F.text == BTN_NEW_TASK)
@router.message(Command("newtask"))
async def cmd_newtask(message: Message, state: FSMContext):
    await state.set_state(TaskCreation.name)
    await message.answer(
        "📝 Please enter the name of your new task:",
        reply_markup=ReplyKeyboardRemove()
    )

# /list or BTN_MY_LIST - show all active tasks with inline buttons
@router.message(F.text == BTN_MY_LIST)
@router.message(Command("list"))
async def cmd_list(message: Message):
    tasks = task_repo.get_tasks(user_id=message.from_user.id)

    if not tasks:
        await message.answer(
            f"📋 Your task list is empty. Use {hbold(BTN_NEW_TASK)} to start.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        return

    for task in tasks:
        text = (
            f"🆔 {task['id']} - {hbold(task['name'])}\n"
            f"📝 {hitalic(task['description'])}\n"
            f"⏰ Due: {task['due_date']}"
        )
        kb = build_task_inline_kb(task['id'])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")

    # Optionally send main menu after the list
    await message.answer("Use the buttons below to manage your tasks.", reply_markup=main_menu_kb())

# FSM for task creation flow
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

# Callback handler for inline buttons
@router.callback_query(F.data.startswith("done:"))
async def callback_done(call: CallbackQuery):
    task_id = int(call.data.split(":")[1])
    user_id = call.from_user.id

    success = task_repo.mark_task_done(task_id, user_id)
    if success:
        await call.answer("Task marked as done!", show_alert=False)
        # Optionally edit the message to show it’s done
        await call.message.edit_text(
            f"{call.message.text}\n\n✅ Marked as done.",
            reply_markup=None  # Remove buttons after done
        )
    else:
        await call.answer("Failed to mark task as done or already done.", show_alert=True)

# Callback handler for delete button
@router.callback_query(F.data.startswith("delete:"))
async def callback_delete(call: CallbackQuery):
    task_id = int(call.data.split(":")[1])
    user_id = call.from_user.id

    success = task_repo.delete_task(task_id, user_id)
    if success:
        await call.answer("Task deleted!", show_alert=False)
        # Delete the message containing the task
        await call.message.delete()
    else:
        await call.answer("Failed to delete task.", show_alert=True)

# Fallback handler for unknown text
@router.message(F.text, StateFilter(None))
async def fallback_message(message: Message):
    await message.answer(
        "I didn't quite catch that. Please use the buttons below to navigate.",
        reply_markup=main_menu_kb()
    )
