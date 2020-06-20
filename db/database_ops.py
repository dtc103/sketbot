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


def add_guild(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int):
    pass


def remove_guild(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int):
    pass


def update_guild(database: mysql.connector.CMySQLConnection, guildname_before: str, guildid_before: int, guildname_after: str, guildid_after: int):
    pass


def get_all_guilds(database: mysql.connector.CMySQLConnection):
    pass


def get_roles(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int):
    pass


def add_role(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int, rolename: str, roleid: int):
    pass


def get_channels(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int):
    pass


def add_channel(database: mysql.connector.CMySQLConnection, guildname: str, guildid: int, rolename: str, roleid: int):
    pass
