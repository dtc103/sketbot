from discord.ext import commands

import sketbot
from db import database_ops

from dotenv import load_dotenv
import os

import sys

import hashlib

import mysql.connector

#TODO database password and username should be passed as command line argument later
#if len(sys.argv) != 2:
#    print("Called script wrong")
#    exit()

load_dotenv()
TOKEN = os.getenv("TOKEN")
USERNAME = os.getenv("DB_USER")
PW = os.getenv("DB_PW")
PICTURE_FOLDER = os.getenv("PICTURE_FOLDER_PATH")

# later add these
daba = database_ops.open_database("localhost", USERNAME, PW, "pictures")

bot = commands.Bot(command_prefix="!")
bot.add_cog(sketbot.IconRandomizerCog(bot, daba, PICTURE_FOLDER))

bot.run(TOKEN)
