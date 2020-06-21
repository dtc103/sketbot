import discord
from discord.ext import commands, tasks

import mysql.connector
from db import database_ops

from PIL import Image
from picture_manipulation.picture_manipualtion import scale_to_discord_icon
import requests
from io import BytesIO

import utilities

import hashlib
import os

from datetime import datetime


class IconRandomizerCog(commands.Cog):
    # bot already has a list with all guilds he is on
    # tmp_pictures = []

    accepted_roles = {} #saved as key value pairs of guild and [(rolename, roleid),..]
    accepted_channels = {} #saved as key value pairs of guild and [(channelname, channelid),..]
    guild_options = {} 

    def __init__(self, bot: commands.Bot, db=None, imagepath:str="C:/"):
        self.bot = bot
        self.database = db
        self.imagepath = imagepath

    @commands.Cog.listener()
    async def on_connect(self):
        pass

    @commands.Cog.listener()
    async def on_resume(self):
        pass

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

        if len(message.attachments) > 0:
            for item in message.attachments:
                self.save_picture(item.url, self.database, message.guild, message.author, message.id)

        if len(message.embeds) > 0:
            for embed in message.embeds:
                self.save_picture(embed.url, self.database, message.guild, message.author, message.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if len(before.embeds) < len(after.embeds):
            for embed in after.embeds:
                self.save_picture(embed.url, self.database,
                                  after.guild, after.author, after.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        '''
            Add entry to database, if joined to new server
        '''
        if guild in self.bot.guilds:
            return

        database_ops.add_guild(self.database, guild.name, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        '''
            remove entry from database, if bot got remove from server
        '''
        if guild in self.bot.guilds:
            database_ops.remove_guild(self.database, guild.name, guild.id)
        

    @commands.Cog.listener()
    async def on_guild_change(self, before: discord.Guild, after: discord.Guild):
        '''
            change entry in database, if guild changed something
        '''
        if before.name != after.name or before.id != after.id:
            database_ops.update_guild(self.database, before.name, before.id, after.name, after.id)
        pass

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        pass

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        pass

    @commands.command(name="addRolename")
    async def add_role(self, ctx: commands.Context, rolename: str):
        '''
            Adds new role to the database(if not already in the database)
        '''
        role: discord.Role = None
        if utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            role = utilities.choose_role(self.bot, ctx, "Type in the index of the role that should be allowed to use this bot")
        else:
            await ctx.send("You dont have the permissions to run this command")
            return

        if (role.name, role.id) in self.accepted_roles[ctx.guild]:

            return

        database_ops.add_role(self.database, ctx.guild.name, ctx.guild.id, role.name, role.id)
        self.accepted_roles[ctx.guild].append((role.name, role.id))

    @commands.command(name="listenOnChannel")
    async def add_listen_channel(self, ctx: commands.Context):
        '''
            if the list for the specific guild is empty, every channel will be accepted.

            Lists all channels and let the user choose from them
        '''
        channelctx:discord.TextChannel = None
        if utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            channelctx = utilities.choose_channel(self.bot, ctx, "Type in the index of the channel, the bot should listen to pictures")
        else:
            await ctx.send("You dont have the permissions to run this command")
            return

        if (channelctx.name, channelctx.id) in self.accepted_roles[ctx.guild]:
            return
        
        database_ops.add_channel(self.database, ctx.guild.name, ctx.guild.id, channelctx.name, channelctx.id)
        self.accepted_channels[ctx.guild].append((channelctx.name, channelctx.id))
        

    @commands.command(name="guildoptions")
    async def change_guild_options(self, ctx:commands.Context):
        """
        changes options like
        """
        pass

    def save_picture(self, url: str, database, guild: discord.Guild, author:discord.User, messageid: int):
        '''
            saves picture to harddrive and database
        '''
        # extract picture out of url
        url_response = requests.get(url)
        bytesio = BytesIO(url_response.content)
        img: Image.Image = Image.open(bytesio)

        # calculate hash of picture to prevent duplicates
        mdfive = hashlib.md5()
        mdfive.update(bytesio.getvalue())
        hash = mdfive.hexdigest()

        #TODO: in the future: decide on database option if this should be compressed or not
        #if self.compress_pictures:
        # discord recommends 512x512 pixel pictures for server icons
        img = scale_to_discord_icon(img)

        imagepath = f"{self.imagepath}/{messageid}.png"

        #TODO: create a new folder for every new guild on harddisk
        if(database.is_connected()):
            is_not_duplicate = database_ops.add_picture(self.database, hash, guild.name, guild.id, author.name, author.id, img.width, img.height, imagepath)
            
            if is_not_duplicate == False:
                return

            try:
                img.save(imagepath, 'png')
            except FileNotFoundError:
                print("Picture save folder not found")