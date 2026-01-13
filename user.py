from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states import UserState
from db import get_test, save_user, save_answer
from config import CHANNELS
from keyboards import subscribe_kb

user_router = Router()


# =========================
# MAJBURIY AZOLIK
# =========================
async def check_subscription(bot, user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except TelegramBadRequest:
            return False
    return True


# =========================
# /start
# =========================
@user_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()

    if not await check_subscription(message.bot, message.from_user.id):
        await message.answer(
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
            reply_markup=subscribe_kb()
        )
        return

    await message.answer("👥 Jamoa nomini kiriting:")
    await state.set_state(UserState.team)


# =========================
# AZOLIKNI QAYTA TEKSHIRISH
# =========================
@user_router.callback_query(lambda c: c.data == "check_sub")
async def check_sub(call: CallbackQuery, state: FSMContext):
    if not await check_subscription(call.bot, call.from_user.id):
        await call.answer("❌ Hali ham obuna emassiz", show_alert=True)
        return

    await call.message.delete()
    await call.message.answer("✅ Obuna tasdiqlandi\n\n👥 Jamoa nomini kiriting:")
    await state.set_state(UserState.team)


# =========================
# JAMOA NOMI
# =========================
@user_router.message(UserState.team)
async def team(message: Message, state: FSMContext):
    team = message.text.strip()

    if len(team) < 2:
        await message.answer("❌ Jamoa nomi juda qisqa")
        return

    await state.update_data(team=team)
    await message.answer("🔐 Test kodini kiriting:")
    await state.set_state(UserState.test_code)


# =========================
# TEST KODI
# =========================
@user_router.message(UserState.test_code)
async def test_code(message: Message, state: FSMContext):
    code = message.text.strip()
    test = await get_test(code)

    if not test:
        await message.answer("❌ Test topilmadi")
        return

    if test[2] == 0:
        await message.answer("⛔ Test hali ochilmagan")
        return

    data = await state.get_data()

    await save_user(
        user_id=message.from_user.id,
        team=data["team"],
        test_code=code
    )

    await state.update_data(test_code=code)

    await message.answer(
        "✅ Testga kirdingiz!\n\n"
        "✍️ Javob yuborish formati:\n"
        "<b>1. A</b>\n<b>2. 25</b>\n<b>3. abC</b>",
        parse_mode="HTML"
    )


# =========================
# JAVOB QABUL QILISH
# =========================
@user_router.message()
async def answers(message: Message, state: FSMContext):
    if not await check_subscription(message.bot, message.from_user.id):
        await message.answer(
            "❗ Davom etish uchun kanallarga obuna bo‘ling:",
            reply_markup=subscribe_kb()
        )
        return

    data = await state.get_data()
    if "test_code" not in data:
        return

    text = message.text.strip()

    # Format: 1. A
    if "." not in text:
        return

    q, ans = text.split(".", 1)

    if not q.strip().isdigit():
        return

    ans = ans.strip()
    if not ans:
        return

    await save_answer(
        user_id=message.from_user.id,
        test_code=data["test_code"],
        question=int(q.strip()),
        answer=ans
    )

    await message.answer(f"✅ {q.strip()}-savol javobi qabul qilindi")
