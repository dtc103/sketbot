import discord
from discord.ext import commands, tasks

import mysql.connector
from sketbot.db import database_ops

from PIL import Image
from sketbot.picture_manipulation.picture_manipualtion import scale_to_discord_icon
import requests
from io import BytesIO

import sketbot.utilities as utilities

import hashlib
import os
import shutil #remove folder even if is empty

from datetime import datetime

from sketbot.exception import InvalidRoleException


class IconRandomizerCog(commands.Cog):
    # bot already has a list with all guilds he is on
    # tmp_pictures = []

    accepted_roles = {} #saved as key value pairs of guild and [(rolename, roleid),..]
    accepted_channels = {} #saved as key value pairs of guild and [(channelname, channelid),..]
    guild_options = {} 

    def __init__(self, bot: commands.Bot, db=None, image_folderpath:str="../pictures"):
        self.bot = bot
        self.database = db
        self.image_folderpath = image_folderpath

    @commands.Cog.listener()
    async def on_connect(self):
        for guild in self.bot.guilds:
            self.create_guild_folder(guild)
            self.accepted_roles[guild] = []
            self.accepted_channels[guild] = []
            self.guild_options[guild] = []

    @commands.Cog.listener()
    async def on_resume(self):
        database_ops.recover_database()
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
        self.create_guild_folder(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        '''
            remove entry from database, if bot got remove from server
        '''
        if guild in self.bot.guilds:
            database_ops.remove_guild(self.database, guild.name, guild.id)
            self.delete_guild_folder(guild)
        

    @commands.Cog.listener()
    async def on_guild_change(self, before: discord.Guild, after: discord.Guild):
        '''
            change entry in database, if guild changed something
        '''
        if before.name != after.name or before.id != after.id:
            database_ops.update_guild(self.database, before.name, before.id, after.name, after.id)
            self.rename_guild_folder(before, after)
        pass

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        database_ops.recover_guild(guild)
        pass

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        await ctx.message.delete(delay=10)
        if isinstance(error.original, InvalidRoleException):
            await ctx.send("You dont have the permissions to run this command", delete_after=10)
        #TODO test, if there will be an exception thrown, when you cannot delete a message, bc you are missing some permissions
        pass

    @commands.command(name="addRolename")
    async def add_role(self, ctx: commands.Context):
        '''
            Adds new role to the database(if not already in the database)
        '''
        role: discord.Role = None
        if await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            role = await utilities.choose_role(self.bot, ctx, "Type in the index of the role that should be allowed to use this bot")
        else:
            raise InvalidRoleException()

        if (role.name, role.id) in self.accepted_roles.get(ctx.guild, None):
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
        if await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            channelctx = utilities.choose_channel(self.bot, ctx, "Type in the index of the channel, the bot should listen to pictures")
        else:
            raise InvalidRoleException()
            

        if (channelctx.name, channelctx.id) in self.accepted_channels[ctx.guild]:
            return
        
        database_ops.add_channel(self.database, ctx.guild.name, ctx.guild.id, channelctx.name, channelctx.id)
        self.accepted_channels[ctx.guild].append((channelctx.name, channelctx.id))
        

    @commands.group(name="options", pass_context=True)
    async def change_guild_options(self, ctx:commands.Context):
        """
        changes options like
        """
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()
        
    
    @change_guild_options.command(name="roles")
    async def change_guild_roles(self, ctx: commands.Context):
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()
        

    @change_guild_options.command(name="save_pictures")
    async def change_save_pictures(self, ctx: commands.Context):
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()

    @change_guild_options.command(name="randomize_server_icon")
    async def randomize_server_icon(self, ctx:commands.Context):
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()

    @change_guild_options.command(name="crop_picture")
    async def crop_picture(self, ctx: commands.Context):
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()

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

        imagepath = f"{self.image_folderpath}/{guild.id}/{messageid}.png"

        if(database.is_connected()):
            try:
                img.save(imagepath, 'png')
                is_not_duplicate = database_ops.add_picture(self.database, hash, guild.name, guild.id, author.name, author.id, img.width, img.height, imagepath)
            
                if is_not_duplicate == False:
                    return
            except FileNotFoundError:
                print("Folder to safe the picture in not found")
            

    def create_guild_folder(self, guild:discord.Guild):
        if not os.path.exists(self.image_folderpath):
            os.mkdir(self.image_folderpath)

        try:
            os.mkdir(f'{self.image_folderpath}/{str(guild.id)}')
        except FileExistsError:
            print(f"{guild.id}: Folder already exists")

    def delete_guild_folder(self, guild:discord.Guild):
        shutil.rmtree(f'{self.image_folderpath}/{str(guild.id)}', ignore_errors=True)

    def rename_guild_folder(self, before: discord.Guild, after: discord.Guild):
        os.rename(f'{self.image_folderpath}/{str(before.id)}', f'{self.image_folderpath}/{str(after.id)}')