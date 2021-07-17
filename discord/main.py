import asyncio
import logging
import os
from pathlib import Path

import aiohttp
import aiosqlite
from dotenv import load_dotenv

import discord
from db_creation import create_db
from db_funcs import check_and_update_nicks, your_leaderboards
from discord.ext import commands
from lt_funcs import check_all_errors, check_your_messsage

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = os.path.join(BASE_DIR, "discord/your_grammar.db")
LOGGER_PATH = os.path.join(BASE_DIR, "logs/discord.log")

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=LOGGER_PATH, encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


async def startup():
    TOKEN = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(
        command_prefix="gb!",
        intents=intents,
        activity=discord.Activity(type=discord.ActivityType.listening, name="gb!help"),
    )

    if os.path.exists(DB_DIR):
        print("I found the db")
    else:
        print("Couldn't find the db - creating one")
        create_db()

    session_timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(
        timeout=session_timeout, trust_env=True
    ) as session:

        bot.session = session

        async with aiosqlite.connect(DB_DIR) as db:

            @bot.event
            async def on_ready():
                print("I am asynchronosouly connected!")

            @bot.event
            async def on_message(msg):
                if msg.author == bot.user:
                    return

                if "your" in msg.content.lower():
                    your_msg = await check_your_messsage(session, db, msg)
                    if your_msg:
                        await msg.reply(your_msg)

                await bot.process_commands(msg)

            @bot.command(name="leaders", help="View the *Your Score* Leaderboards")
            async def leaders(ctx):
                msg = await your_leaderboards(db)
                if msg:
                    await ctx.send(msg)

            @bot.command(
                name="fixme",
                brief="Tries to find any mistake in a message",
                help=(
                    "Needs a message id argument found from right-clicking on any message('Copy ID')"
                    "\nexample: !fixme 000000000011111111"
                ),
            )
            async def fix_me(ctx, msg_id):
                search_limit = 250
                messages = await ctx.channel.history(limit=search_limit).flatten()
                found = False
                for msg in messages:
                    if msg.id == int(msg_id):
                        found = True
                        critique = await check_all_errors(session, msg.content)
                        await ctx.reply(critique)
                        break
                if not found:
                    await ctx.reply(
                        "Sorry - I Couldn't find the message.\n"
                        "*note: I won't find old messages or messages from other channels*"
                    )

            @fix_me.error
            async def fix_me_error(ctx, error):
                if isinstance(
                    error,
                    (commands.CommandInvokeError, commands.MissingRequiredArgument),
                ):
                    await ctx.reply("Error: fixme needs exactly one integer argument")

            @bot.command(
                name="updatenicks",
                help="Checks leaderboards to make sure nicknames are up to date",
            )
            async def update_nicks(ctx):
                resp = await check_and_update_nicks(bot, db)
                if resp:
                    await ctx.send(resp)

            await bot.start(TOKEN)


asyncio.run(startup())
