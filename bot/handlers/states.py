from aiogram.fsm.state import StatesGroup, State

class TaskCreation(StatesGroup):
    """
    Rule 1: Defines the flow for creating a new task.
    """
    name = State()
    description = State()
    due_date = State()

# Love From Mister
