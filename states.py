from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    team_name = State()
    test_code = State()
    answering = State()
