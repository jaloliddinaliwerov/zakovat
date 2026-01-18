from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from states import UserState
from db import get_test, save_answer, get_team_answers
from config import REQUIRED_CHANNELS, ADMIN_IDS

user_router = Router()


# ===============================
# MAJBURIY OBUNA TEKSHIRUV
# ===============================
async def check_subscription(bot, user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except Exception as e:
            print(f"Subscription error: {e}")
            return False
    return True


# ===============================
# /START
# ===============================
@user_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()

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


# ===============================
# JAMOA NOMI
# ===============================
@user_router.message(UserState.team_name)
async def get_team_name(message: Message, state: FSMContext):
    await state.update_data(team=message.text.strip())
    await message.answer("🧪 Test kodini kiriting:")
    await state.set_state(UserState.test_code)


# ===============================
# TEST KODI
# ===============================
@user_router.message(UserState.test_code)
async def get_test_code(message: Message, state: FSMContext):
    test_code = message.text.strip()
    questions_count = get_test(test_code)

    if not questions_count:
        await message.answer("❌ Bunday test topilmadi. Qayta urinib ko‘ring:")
        return

    await state.update_data(
        test=test_code,
        total=questions_count,
        current=1
    )

    await message.answer("1-savolga javob yuboring:")
    await state.set_state(UserState.answering)


# ===============================
# SAVOLLARGA JAVOBLAR
# ===============================
@user_router.message(UserState.answering)
async def process_answers(message: Message, state: FSMContext):
    data = await state.get_data()

    team = data["team"]
    test = data["test"]
    current = data["current"]
    total = data["total"]

    time_now = datetime.now().strftime("%H:%M:%S")

    save_answer(
        team_name=team,
        test_code=test,
        question_number=current,
        answer=message.text,
        time=time_now
    )

    if current < total:
        await state.update_data(current=current + 1)
        await message.answer(f"{current + 1}-savolga javob yuboring:")
        return

    # ===============================
    # HAMMA SAVOLLAR TUGADI
    # ===============================
    answers = get_team_answers(team, test)

    result_text = (
        "📊 <b>TEST NATIJASI</b>\n\n"
        f"🧑‍🤝‍🧑 <b>Jamoa:</b> {team}\n"
        f"🧪 <b>Test:</b> {test}\n\n"
    )

    for q_num, ans, t in answers:
        result_text += (
            f"{q_num}️⃣ <b>Savol</b>\n"
            f"✍️ Javob: {ans}\n"
            f"⏰ Vaqt: {t}\n\n"
        )

    for admin_id in ADMIN_IDS:
        await message.bot.send_message(admin_id, result_text)

    await message.answer("✅ Javoblaringiz qabul qilindi. Rahmat!")
    await state.clear()
