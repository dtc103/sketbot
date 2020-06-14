import mysql.connector
import discord


def open_database(host: str, user: str, password: str, database: str):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    return mydb.cursor()


def add_guild(db_cursor, guild: discord.Guild):
    pass


def remove_guild(db_cursor, guild: discord.Guild):
    pass


def update_guild(db_cursor, guild: discord.Guild):
    pass


def get_all_guilds(db_cursor):
    pass
