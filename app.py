from discord.ext import commands

import sketbot
import database_ops

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
USERNAME = os.getenv("DB_USER")
PW = os.getenv("DB_PW")

# later add these
db_cursor = database_ops.open_database("localhost", USERNAME, PW, "pictures")

bot = commands.Bot(command_prefix="!")
bot.add_cog(sketbot.IconRandomizerCog(bot, db_cursor))

bot.run(TOKEN)
