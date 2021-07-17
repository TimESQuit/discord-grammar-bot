import os
import sqlite3
from pathlib import Path


def create_db():

    BASE_DIR = Path(__file__).resolve().parent
    con = sqlite3.connect(os.path.join(BASE_DIR, "your_grammar.db"))
    cur = con.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id INTEGER PRIMARY KEY,"
        "discord_id INTEGER NOT NULL,"
        "name TEXT NOT NULL,"
        "nick TEXT)"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS errors ("
        "error_id INTEGER PRIMARY KEY,"
        "user_id INTEGER NOT NULL,"
        "datetime TEXT NOT NULL,"
        "message_id INTEGER NOT NULL,"
        "no_of_errors INT NOT NULL,"
        "FOREIGN KEY (user_id) REFERENCES users (user_id)"
        ")"
    )

    cur.execute(
        "CREATE VIEW scores AS "
        "SELECT SUM(errors.no_of_errors) AS score, nick, name, discord_id "
        "FROM users "
        "LEFT JOIN errors on (users.user_id = errors.user_id) "
        "GROUP BY users.user_id "
        "ORDER BY score desc, users.user_id asc "
    )

    con.commit()
    con.close()


if __name__ == "__main__":
    create_db()