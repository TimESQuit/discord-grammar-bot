import datetime
import sqlite3

from tabulate import tabulate


async def handle_your_score(db, msg, matches):
    auth = msg.author
    try:
        cursor = await db.execute(f"SELECT * FROM users WHERE discord_id = {auth.id}")
        if not await cursor.fetchone():
            await db.execute(
                f"INSERT INTO users (discord_id, name, nick)"
                f"VALUES ({auth.id},'{auth.name}','{auth.nick}')"
            )
            await db.commit()
        user_row_query = await db.execute(
            f"SELECT * FROM users WHERE discord_id = {auth.id}"
        )
        user_row = await user_row_query.fetchone()
        await db.execute(
            f"INSERT INTO errors (user_id, datetime, message_id, no_of_errors)"
            f"VALUES ({user_row[0]}, '{datetime.datetime.now()}', {msg.id}, {len(matches)})"
        )
        await db.commit()

        # Check nickname and update if necessary
        nick_q = await db.execute(
            f"SELECT nick, user_id from users WHERE discord_id = {auth.id}"
        )
        nick = await nick_q.fetchone()
        if nick[0] != auth.nick:
            await db.execute(
                f"UPDATE users SET nick = '{auth.nick}' WHERE user_id = {nick[1]}"
            )
            await db.commit()

        # Get new score after db has saved new 'your' error(s)
        updated_score_q = await db.execute(
            f"SELECT score FROM scores WHERE discord_id = {auth.id}"
        )
        up_score = await updated_score_q.fetchone()

        return f"+{len(matches)}: *Your score* is now __**{up_score[0]}**__"

    except sqlite3.OperationalError as e:
        print(f"DB error: {e}")


# 'scores' is a view created by db_creation.create_db()
async def your_leaderboards(db):
    try:
        cursor = await db.execute("SELECT score, nick, name FROM scores")
        rows = await cursor.fetchall()
        tabulated = tabulate(rows, headers=["Your Score", "Nickname", "Username"])
        return f">>> ```{tabulated}```"
    except sqlite3.OperationalError as e:
        print(f"DB error: {e}")


async def check_and_update_nicks(bot, db):
    try:
        cursor = await db.execute("SELECT * FROM users")
        columns = next(zip(*cursor.description))
        discord_id_idx = columns.index("discord_id")
        nick_idx = columns.index("nick")
        users = await cursor.fetchall()
        counter = 0
        for user in users:
            for member in bot.get_all_members():
                if member.id == user[discord_id_idx]:
                    if not (
                        user[nick_idx] == member.nick
                        or (user[nick_idx] == "None" and member.nick == None)
                    ):
                        # I *think* nicknames are the only place that a user could
                        # theoretically insert data into the database. All other info
                        # should be auto-generated/contorlled by discord.
                        # So I tried to take *a* step to prevent sql injection, but I
                        # don't know enough about how sqlite handles this.
                        data = (member.nick, member.id)
                        await db.execute(
                            "UPDATE users SET nick = ? WHERE discord_id = ?", data
                        )
                        await db.commit()
                        counter += 1

        if counter > 1:
            return f"{counter} users were updated"
        elif counter == 1:
            return "1 user was updated"
        else:
            return "No users were updated"
    except sqlite3.OperationalError as e:
        print(f"DB error: {e}")
