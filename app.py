from discord.ext import commands

import sketbot
import database_ops

from dotenv import load_dotenv
import os

import sys

import hashlib

#if len(sys.argv) != 2:
#    print("Called script wrong")
#    exit()

load_dotenv()
TOKEN = os.getenv("TOKEN")
USERNAME = os.getenv("DB_USER")
PW = os.getenv("DB_PW")
print(PW)

#later add these
#db_cursor = database_ops.open_database("localhost", USERNAME, PW, "pictures")

bot = commands.Bot(command_prefix="!")
bot.add_cog(sketbot.IconRandomizerCog(bot))

bot.run(TOKEN)


#if finished -> use hash to check for password
#h = hashlib.sha512()
#h.update(PW.encode("utf-8"))
#print(h.hexdigest())