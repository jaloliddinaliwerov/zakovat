import aiosqlite

DB = "database.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            team TEXT
        );

        CREATE TABLE IF NOT EXISTS tests(
            code TEXT PRIMARY KEY,
            active INTEGER,
            total_questions INTEGER
        );

        CREATE TABLE IF NOT EXISTS questions(
            test_code TEXT,
            q_number INTEGER,
            answer TEXT
        );

        CREATE TABLE IF NOT EXISTS user_answers(
            user_id INTEGER,
            test_code TEXT,
            q_number INTEGER,
            answer TEXT
        );

        CREATE TABLE IF NOT EXISTS team_scores(
            team TEXT PRIMARY KEY,
            score INTEGER
        );
        """)
        await db.commit()
