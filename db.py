import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tests (
    test_code TEXT PRIMARY KEY,
    questions_count INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS answers (
    team_name TEXT,
    test_code TEXT,
    question_number INTEGER,
    answer TEXT,
    time TEXT
)
""")

conn.commit()


def create_test(code, count):
    cursor.execute(
        "INSERT OR REPLACE INTO tests VALUES (?,?)",
        (code, count)
    )
    conn.commit()


def get_test(code):
    cursor.execute(
        "SELECT questions_count FROM tests WHERE test_code=?",
        (code,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def save_answer(team, test, q_num, answer, time):
    cursor.execute(
        "INSERT INTO answers VALUES (?,?,?,?,?)",
        (team, test, q_num, answer, time)
    )
    conn.commit()


def get_team_answers(team, test):
    cursor.execute(
        "SELECT question_number, answer, time FROM answers WHERE team_name=? AND test_code=? ORDER BY question_number",
        (team, test)
    )
    return cursor.fetchall()
