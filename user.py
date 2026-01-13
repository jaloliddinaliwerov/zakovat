from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states import UserState
from db import get_test, save_user, save_answer
from config import CHANNELS
from keyboards import subscribe_kb

user_router = Router()

async def check_subscription(bot, user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except TelegramBadRequest:
            return False
    return True

@user_router.message(commands=["start"])
async def start(message: Message, state: FSMContext):
    if not await check_subscription(message.bot, message.from_user.id):
        await message.answer("❗ Kanallarga obuna bo‘ling:", reply_markup=subscribe_kb())
        return
    await message.answer("Jamoa nomini kiriting:")
    await state.set_state(UserState.team)

@user_router.callback_query(lambda c: c.data == "check_sub")
async def check_sub(call: CallbackQuery, state: FSMContext):
    if not await check_subscription(call.bot, call.from_user.id):
        await call.answer("❌ Obuna bo‘ling", show_alert=True)
        return
    await call.message.delete()
    await call.message.answer("✅ Tasdiqlandi\nJamoa nomini kiriting:")
    await state.set_state(UserState.team)

@user_router.message(UserState.team)
async def team(message: Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer("Test kodini kiriting:")
    await state.set_state(UserState.test_code)

@user_router.message(UserState.test_code)
async def test_code(message: Message, state: FSMContext):
    test = await get_test(message.text)
    if not test or test[2] == 0:
        await message.answer("⛔ Test yopiq yoki mavjud emas")
        return
    data = await state.get_data()
    await save_user(message.from_user.id, data["team"], message.text)
    await state.update_data(test_code=message.text)
    await message.answer("✅ Javob yuboring\nMasalan: 1. A")

@user_router.message()
async def answers(message: Message, state: FSMContext):
    if not await check_subscription(message.bot, message.from_user.id):
        await message.answer("❗ Kanallarga obuna bo‘ling", reply_markup=subscribe_kb())
        return

    text = message.text.strip()
    if "." not in text:
        return

    q, ans = text.split(".", 1)
    if not q.strip().isdigit():
        return

    data = await state.get_data()
    if "test_code" not in data:
        return

    await save_answer(
        message.from_user.id,
        data["test_code"],
        int(q.strip()),
        ans.strip()
    )
    await message.answer("✅ Qabul qilindi")
