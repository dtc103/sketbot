from discord.ext import commands

import sketbot.sketbot as sb
from sketbot.db import database_ops

from dotenv import load_dotenv
import os

import sys

import hashlib

import mysql.connector


def test_database_function(database):
    dabacu = database.cursor()
    
    dabacu.execute("delete from channels;")
    dabacu.execute("delete from pictable;")
    dabacu.execute("delete from roles")
    dabacu.execute("delete from guildoptions")
    
    try:
        dabacu.execute("insert into channels (guildid, guildname, channelid, channelname) values (\"123\", \"name\", \"321\", \"cname\");")
        dabacu.execute("insert into channels (guildid, guildname, channelid, channelname) values (\"123\", \"name\", \"321134\", \"cname\");")
        dabacu.execute("insert into roles (guildid, guildname, roleid, rolename) values (\"123\", \"name\", \"321\", \"cname\");")
        dabacu.execute("insert into pictable (pichash, guildid, guildname, authorid, authorname, date, width, height, picpath) values (\"1234143524325\", \"123\", \"name\", \"132432\", \"name of author\", \"2013-02-02\", 144, 200, \"picpath/newpath/newpath\");")
        dabacu.execute("insert into guildoptions (guildid, guildname, crop_picture, safe_pictures, random_icon_change) values (\"123\", \"name\", false, false, false);")
    except mysql.connector.errors.IntegrityError:
        print("duplicate entry")

    database.commit()
    
    #database_ops.update_guild(database, "name", 123, "new_name", 123)
    database_ops.remove_guild(database, "name", 123)
    
    #dabacu.execute("select * from channels where channelid=\"321\"")
    # for gid, gname, cid, cname in dabacu.fetchall():
    #     print(gid, gname, cid, cname)

    dabacu.execute("show tables")
    for table in dabacu.fetchall():
        print(table[0])

    exit(-1)



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


test_database_function(daba)


bot = commands.Bot(command_prefix="!")
bot.add_cog(sb.IconRandomizerCog(bot, daba))

bot.run(TOKEN)


