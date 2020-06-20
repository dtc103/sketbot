import discord
from discord.ext import commands, tasks

import mysql.connector
import database_ops

from PIL import Image
import requests
from io import BytesIO

import hashlib
import os

from datetime import datetime

import database_ops


class IconRandomizerCog(commands.Cog):
    # bot hat schon ne list, in der alle gilden drin stehen
    # tmp_pictures = []
    accepted_roles = {}
    accepted_channels = {}

    def __init__(self, bot: commands.Bot, db=None):
        self.bot = bot
        self.database = db

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
            react on messages and checks if it contains a valid picture.
            First the picture gets add to the tmp_picturelist and then to the database if the list contains more than 10 pictures
        '''
        if message.author == self.bot:
            return

        if message.author.bot:
            return

        print("Message sent by:", message.author.name)

        if len(message.attachments) > 0:
            for item in message.attachments:
                self.save_picture(item.url, self.database, message.guild)

        if len(message.embeds) > 0:
            for embed in message.embeds:
                self.save_picture(embed.url, self.database, message.guild)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if len(before.embeds) < len(after.embeds):
            for embed in after.embeds:
                self.save_picture(embed.url, self.database, after.guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''
            Add table to database, if joined to new server
        '''
        if guild in tmp_guilds:
            return

        add_guild(self.database, guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''
            remove table to database, if bot got remove from server
        '''
        remove_guild(self.database, guild)
        pass

    @commands.Cog.listener()
    async def on_guild_change(self, before: discord.Guild, after: discord.Guild):
        '''
            change entry in database, if guild changed something
        '''
        if before.name != after.name:
            database_ops.update_guild(self.database, before, after)
        pass

    @commands.Cog.listener()
    async def on_connect(self):
        pass

    @commands.Cog.listener()
    async def on_resume(self):
        pass

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        pass

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        pass

    @commands.command()
    async def add_role(self, ctx: commands.Context):
        '''
            Lists all roles to choose from and adds it to the database afterwards(if not already in the database)
        '''
        pass

    @commands.command()
    async def add_role(self, ctx: commands.Context, rolename: str):
        '''
            Adds new role to the database(if not already in the database)
        '''
        # check if rolename is valid on the server
        pass

    @commands.command()
    async def add_channel(self, ctx: commands.Context):
        '''
            if the list for the specific guild is empty, every channel will be accepted.

            Lists all channels and let the user choose from them
        '''
        pass

    @commands.command()
    async def add_channel(self, ctx: commands.Context, channelname: str):
        '''
            If the list for the specific guild is empty, ever channel will be accepted.

            Adds the channelname to the restrictions
        '''
        pass

    def save_picture(self, url: str, database, guild: discord.Guild):
        '''
            saves picture to harddrive and database
        '''
        url_response = requests.get(url)
        bytesio = BytesIO(url_response.content)
        img: Image.Image = Image.open(bytesio)

        mdfive = hashlib.md5()
        mdfive.update(bytesio.getvalue())
        hash = mdfive.hexdigest()

        img = self.scale_to_discord_icon(img)

        imagepath = f"C:/Users/Jan-K/programming/python/discord_bot/sketbot/pictures/{os.path.basename(url)}.png"

        # TODO noch geeigneten Namen für die bilder finden
        img.save(imagepath, 'png')

        if(database.is_connected()):
            database_cursor = database.cursor()

            insert_statement = (
                'insert into pictable (pichash, guildname, guildid, date, width, height, picpath) VALUES (%s, %s, %s, %s, %s, %s, %s);')

            params = (str(hash), str(guild.name), str(guild.id), str(datetime.today(
            ).strftime('%Y-%m-%d')), int(img.width), int(img.height), imagepath)

    def scale_to_discord_icon(self, img: Image.Image):
        maxpix = 512

        rawheight = img.height
        rawwidth = img.width

        if rawheight > rawwidth:
            ratio = float(maxpix) / float(rawheight)
            pass
        else:
            ratio = float(maxpix) / float(rawwidth)
            pass

        newheight = int(rawheight * ratio)
        newwidth = int(rawwidth * ratio)

        return img.resize((newwidth, newheight), Image.ANTIALIAS)
