import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            code TEXT PRIMARY KEY,
            active INTEGER
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
        CREATE TABLE IF NOT EXISTS questions (
            test_code TEXT,
            question_number INTEGER,
            correct_answer TEXT,
            PRIMARY KEY (test_code, question_number)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id INTEGER,
            test_code TEXT,
            question_number INTEGER,
            answer TEXT,
            is_correct INTEGER
        )
        """)
        await db.commit()


# -------- TEST --------
async def create_test(code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM tests WHERE code=?", (code,))
        await db.execute(
            "INSERT INTO tests VALUES (?, 0)",
            (code,)
        )
        await db.commit()

async def set_test_active(code: str, active: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE tests SET active=? WHERE code=?",
            (active, code)
        )
        await db.commit()

async def get_test(code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT code, active FROM tests WHERE code=?",
            (code,)
        )
        return await cur.fetchone()


# -------- QUESTIONS --------
async def add_question(test_code: str, q_number: int, correct: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR REPLACE INTO questions
        VALUES (?, ?, ?)
        """, (test_code, q_number, correct.lower()))
        await db.commit()

async def get_correct_answer(test_code: str, q_number: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("""
        SELECT correct_answer FROM questions
        WHERE test_code=? AND question_number=?
        """, (test_code, q_number))
        row = await cur.fetchone()
        return row[0] if row else None


# -------- USERS & ANSWERS --------
async def save_user(user_id, team, test_code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users VALUES (?, ?, ?)
        """, (user_id, team, test_code))
        await db.commit()

async def save_answer(user_id, test_code, q_number, answer, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO answers VALUES (?, ?, ?, ?, ?)
        """, (user_id, test_code, q_number, answer, is_correct))
        await db.commit()
