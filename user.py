from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import UserState
from db import get_test, save_user, save_answer, get_correct_answer

user_router = Router()


@user_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👥 Jamoa nomini kiriting:")
    await state.set_state(UserState.team)


@user_router.message(UserState.team)
async def team(message: Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer("🔐 Test kodini kiriting:")
    await state.set_state(UserState.test_code)


@user_router.message(UserState.test_code)
async def test_code(message: Message, state: FSMContext):
    test = await get_test(message.text)
    if not test or test[1] == 0:
        await message.answer("⛔ Test yopiq")
        return

    data = await state.get_data()
    await save_user(message.from_user.id, data["team"], message.text)
    await state.update_data(test_code=message.text)

    await message.answer(
        "✅ Test boshlandi\n"
        "Javob yuboring:\n"
        "Masalan: 1. A"
    )


@user_router.message()
async def answers(message: Message, state: FSMContext):
    data = await state.get_data()
    if "test_code" not in data:
        return

    if "." not in message.text:
        return

    q, ans = message.text.split(".", 1)
    if not q.strip().isdigit():
        return

    q_num = int(q.strip())
    ans = ans.strip().lower()

    correct = await get_correct_answer(data["test_code"], q_num)
    is_correct = 1 if correct and ans == correct else 0

    await save_answer(
        message.from_user.id,
        data["test_code"],
        q_num,
        ans,
        is_correct
    )

    await message.answer("✅ To‘g‘ri" if is_correct else "❌ Noto‘g‘ri")
