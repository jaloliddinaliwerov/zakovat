from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    team = State()
    test_code = State()
    answering = State()
