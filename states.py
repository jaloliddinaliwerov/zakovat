from aiogram.fsm.state import StatesGroup, State

class UserState(StatesGroup):
    team = State()
    test_code = State()
