from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import CHANNELS
from states import UserState
from keyboards import sub_kb
from db import save_user, test_open, save_answer, already_answered

user_router = Router()

@user_router.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    await msg.answer("Avval obuna bo‘ling:", reply_markup=sub_kb(CHANNELS))

@user_router.callback_query(F.data == "check_sub")
async def check(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Jamoa nomini kiriting:")
    await state.set_state(UserState.team)

@user_router.message(UserState.team)
async def team(msg: Message, state: FSMContext):
    await save_user(msg.from_user.id, msg.text)
    await msg.answer("Test kodini kiriting:")
    await state.set_state(UserState.test_code)

@user_router.message(UserState.test_code)
async def code(msg: Message, state: FSMContext):
    if not await test_open(msg.text):
        await msg.answer("❌ Test yopiq")
        return
    await state.update_data(test=msg.text)
    await msg.answer("✍️ Javob yuboring:\n1 A")
    await state.clear()

@user_router.message()
async def answer(msg: Message, state: FSMContext):
    try:
        q, ans = msg.text.split(maxsplit=1)
        q = int(q)
    except:
        return

    data = await state.get_data()
    code = data.get("test")
    if not code:
        return

    if await already_answered(msg.from_user.id, code, q):
        await msg.answer("❌ Bu savolga javob berilgan")
        return

    await save_answer(msg.from_user.id, code, q, ans)
    await msg.answer("✅ Qabul qilindi")
