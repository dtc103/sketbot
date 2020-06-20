import mysql.connector
import discord


def open_database(host: str, user: str, password: str, database: str):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    return mydb


def add_guild(databse, guild: discord.Guild):
    pass


def remove_guild(databse, guild: discord.Guild):
    pass


def update_guild(databse, before: discord.Guild, after: discord.Guild):
    pass


def get_all_guilds(databse):
    pass


def get_roles(databse, guild: discord.Guild):
    pass


def add_role(databse, guild, role: discord.Role):
    pass


def get_channels(database, guild: discord.Guild):
    pass


def add_channel(databse, guild, channel: discord.TextChannel):
    pass
