import aiosqlite

DB = "database.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            code TEXT PRIMARY KEY,
            is_open INTEGER
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            test_code TEXT,
            q_num INTEGER,
            correct TEXT,
            PRIMARY KEY (test_code, q_num)
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id INTEGER,
            test_code TEXT,
            q_num INTEGER,
            answer TEXT,
            is_correct INTEGER,
            PRIMARY KEY (user_id, test_code, q_num)
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            team TEXT
        )""")
        await db.commit()
async def create_test(code):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR REPLACE INTO tests VALUES (?,0)", (code,))
        await db.commit()

async def open_test(code, val):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE tests SET is_open=? WHERE code=?", (val, code))
        await db.commit()

async def test_open(code):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT is_open FROM tests WHERE code=?", (code,))
        r = await cur.fetchone()
        return r and r[0] == 1

async def add_question(code, q, correct):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO questions VALUES (?,?,?)",
            (code, q, correct.lower())
        )
        await db.commit()

async def save_user(uid, team):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (uid, team))
        await db.commit()

async def already_answered(uid, code, q):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT 1 FROM answers WHERE user_id=? AND test_code=? AND q_num=?",
            (uid, code, q)
        )
        return await cur.fetchone() is not None

async def save_answer(uid, code, q, ans):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT correct FROM questions WHERE test_code=? AND q_num=?",
            (code, q)
        )
        row = await cur.fetchone()
        correct = row and row[0] == ans.lower()
        await db.execute(
            "INSERT INTO answers VALUES (?,?,?,?,?)",
            (uid, code, q, ans, int(correct))
        )
        await db.commit()
