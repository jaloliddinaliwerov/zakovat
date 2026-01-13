from aiogram import Router, F
from aiogram.types import Message
from config import ADMINS
import aiosqlite
from db import DB

admin_router = Router()

def is_admin(uid):
    return uid in ADMINS

@admin_router.message(Command("open_question"))
async def open_question(message: Message):
    await message.answer("🟢 open_question handler ishladi")


@admin_router.message(F.text.startswith("/add_test"))
async def add_test(message: Message):
    if not is_admin(message.from_user.id):
        return
    _, code, total = message.text.split()
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO tests VALUES(?,?,?,?)",
            (code, 0, int(total), 0)
        )
        await db.commit()
    await message.answer("✅ Test yaratildi")


@admin_router.message(F.text.startswith("/add_question"))
async def add_question(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, code, qn, ans = message.text.split()
    except:
        await message.answer("❌ Format: /add_question TEST 1 A1")
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO questions VALUES(?,?,?)",
            (code, int(qn), ans)
        )
        await db.commit()
    await message.answer("✅ Savol qo‘shildi")

@admin_router.message(F.text.startswith("/open_question"))
async def open_question(message: Message):
    if message.from_user.id not in ADMINS:
        return

    _, code, qn = message.text.split()
    qn = int(qn)

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE tests SET current_question=? WHERE code=? AND active=1",
            (qn, code)
        )
        await db.commit()

    await message.answer(f"📢 {qn}-savol OCHILDI\nUserlar javob yuborishi mumkin")

@admin_router.message(F.text.startswith("/close_question"))
async def close_question(message: Message):
    if message.from_user.id not in ADMINS:
        return

    code = message.text.split()[1]

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE tests SET current_question=0 WHERE code=?",
            (code,)
        )
        await db.commit()

    await message.answer("⛔ Savol yopildi")

@admin_router.message(F.text.startswith("/start_test"))
async def start_test(message: Message):
    if not is_admin(message.from_user.id):
        return
    code = message.text.split()[1]
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE tests SET active=1 WHERE code=?", (code,))
        await db.commit()
    await message.answer("🚀 Test boshlandi\nJavoblarni 1,2,3 tartibda yuboring")


@admin_router.message(F.text.startswith("/finish_test"))
async def finish_test(message: Message):
    if not is_admin(message.from_user.id):
        return
    code = message.text.split()[1]

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT ua.user_id, ua.q_number, ua.answer, q.answer
        FROM user_answers ua
        JOIN questions q
        ON ua.test_code=q.test_code AND ua.q_number=q.q_number
        WHERE ua.test_code=?
        """, (code,))
        rows = await cur.fetchall()

        for user_id, qn, u_ans, c_ans in rows:
            if u_ans == c_ans:
                await db.execute("""
                UPDATE team_scores SET score=score+1
                WHERE team=(SELECT team FROM users WHERE user_id=?)
                """, (user_id,))

        await db.execute("UPDATE tests SET active=0 WHERE code=?", (code,))
        await db.commit()

    await message.answer("🏁 Test yakunlandi\n📊 Reytingni /rating bilan ko‘ring")


@admin_router.message(F.text == "/rating")
async def rating(message: Message):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT team, score FROM team_scores ORDER BY score DESC"
        )
        rows = await cur.fetchall()

    text = "🏆 JAMOALAR REYTINGI 🏆\n\n"
    for i, (team, score) in enumerate(rows, 1):
        text += f"{i}. {team} — {score} ball\n"

    await message.answer(text)
