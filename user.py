from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import UserState
import aiosqlite
from db import DB
import re

user_router = Router()

from config import ADMINS

@user_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer(
            "👑 ADMIN PANEL\n\n"
            "/add_test KOD N — test yaratish\n"
            "/add_question KOD № JAVOB — savol qo‘shish\n"
            "/start_test KOD — testni boshlash\n"
            "/finish_test KOD — testni tugatish\n"
            "/rating — reyting"
        )
        await state.clear()
    else:
        await message.answer("Jamoa nomini kiriting:")
        await state.set_state(UserState.team)

@user_router.message()
async def answer_handler(message: Message, state: FSMContext):
    text = message.text.strip()

    # faqat "1. A" yoki "1 A" formatni qabul qilamiz
    if "." in text:
        parts = text.split(".", 1)
    else:
        parts = text.split(" ", 1)

    if len(parts) != 2:
        await message.answer("❌ Format noto‘g‘ri. Masalan: 1. A")
        return

    q_part, answer = parts

    if not q_part.strip().isdigit():
        await message.answer("❌ Savol raqami son bo‘lishi kerak")
        return

    q_number = int(q_part.strip())
    answer = answer.strip()

    data = await state.get_data()
    test_code = data.get("test_code")

    if not test_code:
        await message.answer("❌ Avval test kodini kiriting")
        return

    test = await get_test(test_code)
    if not test or test["active"] == 0:
        await message.answer("⛔ Test yopiq")
        return

    await save_answer(
        user_id=message.from_user.id,
        test_code=test_code,
        question_number=q_number,
        answer=answer
    )

    await message.answer(f"✅ {q_number}-savol javobi qabul qilindi")



@user_router.message(UserState.team)
async def team_set(message: Message, state: FSMContext):
    team = message.text.strip()
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users VALUES(?,?,?)",
            (message.from_user.id, message.from_user.username, team)
        )
        await db.execute(
            "INSERT OR IGNORE INTO team_scores VALUES(?,0)",
            (team,)
        )
        await db.commit()
    await message.answer("Test kodini kiriting:")
    await state.set_state(UserState.test_code)


@user_router.message(UserState.test_code)
async def test_code_set(message: Message, state: FSMContext):
    code = message.text.strip()
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT active, total_questions FROM tests WHERE code=?",
            (code,)
        )
        test = await cur.fetchone()
        if not test or test[0] == 0:
            await message.answer("❌ Test faol emas")
            return

    await state.update_data(test_code=code)
    await state.set_state(UserState.answering)
    await message.answer(
        "✍️ Javoblarni yuboring:\nMasalan: 1. A"
    )


@user_router.message(UserState.answering)
async def answer(message: Message, state: FSMContext):
    text = message.text.strip()

    # 1. Javob formati: 1. A / 1 A / 1-A
    import re
    match = re.match(r"(\d+)\D+(.+)", text)
    if not match:
        await message.answer("❌ Format noto‘g‘ri. Masalan: 1. A")
        return

    qn = int(match.group(1))
    ans = match.group(2).strip()

    data = await state.get_data()
    code = data.get("test_code")

    if not code:
        await message.answer("❌ Test kodi topilmadi")
        return

    import aiosqlite
    from db import DB

    async with aiosqlite.connect(DB) as db:
        # 2. Test holatini tekshiramiz
        cur = await db.execute(
            "SELECT active, current_question FROM tests WHERE code=?",
            (code,)
        )
        row = await cur.fetchone()

        if not row or row[0] == 0:
            await message.answer("⛔ Test faol emas")
            return

        current_q = row[1]

        # 3. Savol ochiqmi?
        if current_q == 0:
            await message.answer("⛔ Hozir savol yopiq")
            return

        # 4. To‘g‘ri savol raqamimi?
        if qn != current_q:
            await message.answer(f"❌ Hozir {current_q}-savol ochiq")
            return

        # 5. Javobni saqlaymiz
        await db.execute(
            "INSERT OR REPLACE INTO user_answers VALUES(?,?,?,?)",
            (message.from_user.id, code, qn, ans)
        )
        await db.commit()

    await message.answer(f"✅ {qn}-savol javobi qabul qilindi")
        
