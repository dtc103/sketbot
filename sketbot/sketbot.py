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
import shutil #remove folder even if its not empty

from datetime import datetime

from sketbot.exception import InvalidRoleException


class IconRandomizerCog(commands.Cog):
    # bot already has a list with all guilds he is on
    # tmp_pictures = []

    accepted_roles = {} #saved as key value pairs of guild and [(rolename, roleid),..]
    listen_channels = {} #saved as key value pairs of guild and [(channelname, channelid),..]
    guild_options = {} #dictionary of dictionaries with its option values

    def __init__(self, bot: commands.Bot, db=None, image_folderpath:str="../pictures"):
        self.bot = bot
        self.database = db
        self.image_folderpath = image_folderpath

    @commands.Cog.listener()
    async def on_connect(self):
        pass
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.create_guild_folder(guild)
            self.accepted_roles[guild] = []
            self.listen_channels[guild] = []
            self.guild_options[guild] = []
        #database_ops.recover_from_database()

    @commands.Cog.listener()
    async def on_disconnect(self):
        for guild in self.bot.guilds:
            del self.accepted_roles[guild]
            del self.listen_channels[guild]
            del self.guild_options[guild]

    @commands.Cog.listener()
    async def on_resumed(self):
        print("RESUMED")
        #database_ops.recover_from_database()
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

        self.guild_options[guild] = {"crop_picture": True, "safe_picture": False, "random_icon_change": False}

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        '''
            remove entry from database, if bot got removed from server
        '''
        if guild in self.bot.guilds:
            database_ops.remove_guild(self.database, guild.name, guild.id)
            self.delete_guild_folder(guild)
            del self.listen_channels[guild]
            del self.accepted_roles[guild]
            del self.guild_options[guild]

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
        print(f"{guild.name} is available")
        #database_ops.recover_guild(guild)
        pass

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        '''
        If the guild gets unavailable, just delete it from the cache.
        It will be recovered afterwards in the on_guild_available method
        and the last valid state will be loaded in the cache
        '''
        del self.listen_channels[guild]
        del self.accepted_roles[guild]
        del self.guild_options[guild]
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            print("Error: CommandNotFound was called")
            return

        await ctx.message.delete(delay=10)
        if isinstance(error.original, InvalidRoleException):
            await ctx.send(f"{ctx.message.author.mention}, you dont have the permissions to run this command", delete_after=10)
            return 
        #TODO test, if there will be an exception thrown, when the bot cannot delete a message or a command, bc you are missing some permissions
        pass

    
    @commands.command(name="addRolename")
    async def add_role(self, ctx: commands.Context):
        '''
            Adds new role to the database(if not already in the database)
        '''
        role: discord.Role = None
        if await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            role = await utilities.choose_role(self.bot, ctx, "Type in the index of the role that should be allowed to use this bot", timeout=20)
        else:
            raise InvalidRoleException()

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

        if await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            channelctx = await utilities.choose_channel(self.bot, ctx, "Type in the index of the channel, the bot should listen to pictures in", 20)
        else:
            raise InvalidRoleException()
            
        if (channelctx.name, channelctx.id) in self.listen_channels[ctx.guild]:
            return
        
        database_ops.add_channel(self.database, ctx.guild.name, ctx.guild.id, channelctx.name, channelctx.id)
        self.listen_channels[ctx.guild].append((channelctx.name, channelctx.id))
        

    @commands.group(name="options", pass_context=True)
    async def change_guild_options(self, ctx:commands.Context):
        """
        changes options like
        """
        if not await utilities.has_role(ctx.author, self.accepted_roles[ctx.guild]):
            raise InvalidRoleException()
        
    @change_guild_options.command(name="safe_pictures")
    async def change_save_pictures(self, ctx: commands.Context):
        if utilities.wait_for_query(self.bot, ctx, "To enable/disable the saving of the pictures press ✔️ to enable or ❌ to disable it", None, 20):
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, safe_picture=True)
            self.guild_options[ctx.guild]["safe_picture"] = True
        else:
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, safe_picture=False)
            self.guild_options[ctx.guild]["safe_picture"] = False

    @change_guild_options.command(name="randomize_server_icon")
    async def randomize_server_icon(self, ctx:commands.Context):
        if utilities.wait_for_query(self.bot, ctx, "To enable/disable the randomization of the server icon press ✔️ to enable or ❌ to disable it", None, 20):
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, random_icon_change=True)
            self.guild_options[ctx.guild]["random_icon_change"] = True
        else:
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, random_icon_change=False)
            self.guild_options[ctx.guild]["random_icon_change"] = False
        pass

    @change_guild_options.command(name="crop_picture")
    async def crop_picture(self, ctx: commands.Context):
        if utilities.wait_for_query(self.bot, ctx, "If you want that every picture will get compressed to the recommended size of a discord server icon press ✔️ to enable or ❌ to disable it", None, 20):
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, crop_picture=True)
            self.guild_options[ctx.guild]["crop_picture"] = True
        else:
            database_ops.update_guild_options(self.database, ctx.guild.name, ctx.guild.id, crop_picture=False)
            self.guild_options[ctx.guild]["crop_picture"] = False
        pass

    @change_guild_options.command(name="deleteRole")
    async def change_guild_roles(self, ctx: commands.Context):
        
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
        if self.guild_options[guild]["crop_picture"]:
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


    