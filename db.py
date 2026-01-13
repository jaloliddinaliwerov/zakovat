import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            code TEXT PRIMARY KEY,
            questions INTEGER,
            active INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            team TEXT,
            test_code TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id INTEGER,
            test_code TEXT,
            question INTEGER,
            answer TEXT
        )
        """)
        await db.commit()

# ---------- TEST ----------
async def create_or_reset_test(code, questions):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM tests WHERE code=?", (code,))
        await db.execute("DELETE FROM answers WHERE test_code=?", (code,))
        await db.execute(
            "INSERT INTO tests (code, questions, active) VALUES (?, ?, 0)",
            (code, questions)
        )
        await db.commit()

async def set_test_active(code, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE tests SET active=? WHERE code=?",
            (value, code)
        )
        await db.commit()

async def get_test(code):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT code, questions, active FROM tests WHERE code=?",
            (code,)
        )
        return await cur.fetchone()

# ---------- USER ----------
async def save_user(user_id, team, test_code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO users (user_id, team, test_code) VALUES (?, ?, ?)",
            (user_id, team, test_code)
        )
        await db.commit()

async def save_answer(user_id, test_code, question, answer):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO answers VALUES (?, ?, ?, ?)",
            (user_id, test_code, question, answer)
        )
        await db.commit()

# ---------- RATING ----------
async def get_rating(test_code):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        SELECT u.team, COUNT(a.question) AS score
        FROM answers a
        JOIN users u ON u.user_id = a.user_id
        WHERE a.test_code=?
        GROUP BY u.team
        ORDER BY score DESC
        LIMIT 10
        """, (test_code,))
        return await cur.fetchall()
