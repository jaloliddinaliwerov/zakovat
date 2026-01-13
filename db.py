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
