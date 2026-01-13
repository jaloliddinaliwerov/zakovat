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
    match = re.match(r"(\d+)\D+(.+)", text)
    if not match:
        await message.answer("❌ Format noto‘g‘ri: 1. A")
        return

    qn = int(match.group(1))
    ans = match.group(2).strip()
    data = await state.get_data()
    code = data["test_code"]

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT total_questions FROM tests WHERE code=?",
            (code,)
        )
        total = (await cur.fetchone())[0]

        if qn > total:
            await message.answer("❌ Bunday savol yo‘q")
            return

        await db.execute(
            "INSERT OR REPLACE INTO user_answers VALUES(?,?,?,?)",
            (message.from_user.id, code, qn, ans)
        )
        await db.commit()

    if qn == total:
        await message.answer(
            "✅ Barcha javoblar qabul qilindi\nNatijalarni kuting"
        )
    else:
        await message.answer(f"☑️ {qn}-savol qabul qilindi")
