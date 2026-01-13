from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    team = State()
    test_code = State()

class AdminState(StatesGroup):
    create_test = State()
    add_question = State()
