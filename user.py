from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from states import UserState
from db import get_test, save_answer, get_team_answers
from config import ADMIN_IDS

user_router = Router()

async def check_subscription(bot, user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False
    return True

@user_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    subscribed = await check_subscription(
        message.bot,
        message.from_user.id
    )

    if not subscribed:
        text = "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n\n"
        for ch in REQUIRED_CHANNELS:
            text += f"👉 {ch}\n"

        text += "\n✅ Obuna bo‘lgach /start ni qayta bosing"
        await message.answer(text)
        return

    await message.answer(
        "👋 Botga xush kelibsiz!\n\n"
        "🧑‍🤝‍🧑 Jamoa nomini kiriting:"
    )
    await state.set_state(UserState.team_name)


@user_router.message(UserState.team_name)
async def get_team(message: Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer("🧪 Test kodini kiriting:")
    await state.set_state(UserState.test_code)

@user_router.message(UserState.test_code)
async def get_test_code(message: Message, state: FSMContext):
    test_code = message.text
    count = get_test(test_code)

    if not count:
        await message.answer("❌ Test topilmadi")
        return

    await state.update_data(
        test=test_code,
        total=count,
        current=1
    )

    await message.answer("1-savolga javob yuboring:")
    await state.set_state(UserState.answering)

@user_router.message(UserState.answering)
async def process_answers(message: Message, state: FSMContext):
    data = await state.get_data()

    team = data["team"]
    test = data["test"]
    q = data["current"]
    total = data["total"]

    now = datetime.now().strftime("%H:%M:%S")

    save_answer(team, test, q, message.text, now)

    if q < total:
        await state.update_data(current=q+1)
        await message.answer(f"{q+1}-savolga javob yuboring:")
    else:
        answers = get_team_answers(team, test)

        text = (
            "📊 TEST NATIJASI\n\n"
            f"🧑‍🤝‍🧑 Jamoa: {team}\n"
            f"🧪 Test: {test}\n\n"
        )

        for qn, ans, t in answers:
            text += (
                f"{qn}️⃣ Savol\n"
                f"Javob: {ans}\n"
                f"⏰ {t}\n\n"
            )

        for admin in ADMIN_IDS:
            await message.bot.send_message(admin, text)

        await message.answer("✅ Javoblaringiz qabul qilindi")
        await state.clear()
