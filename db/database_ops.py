import mysql.connector
from datetime import datetime


def open_database(host: str, user: str, password: str, database: str):
    """
    Opens the specified database and returns its handle
    """
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    return mydb


def add_guild(database, guildname: str, guildid: int):
    """
    Add guild to guild table with options
    """
    
    pass


def remove_guild(database, guildname: str, guildid: int):
    """
    remove everything from that guild in every table and return every picturepath to delete on hardisk
    """
    pass


def update_guild(database, guildname_before: str, guildid_before: int, guildname_after: str, guildid_after: int):
    """
    Updates a guild if there were some changes on the discord guild
    """
    pass


def get_all_guilds(database):
    """
    returns a list of guilds the bot is active on
    """
    pass


def get_roles(database, guildname: str, guildid: int):
    """
    Returns all discord roles for a specific guild
    """
    database_cursor = database.cursor()


    pass


def add_role(database, guildname: str, guildid: int, rolename: str, roleid: int):
    """
    Adds a discord role to the database
    create table roles(
        guildid,
        guildname,
        roleid,
        rolename
    )
    """
    database_cursor = database.cursor()

    role_insert_stmt = ("insert into roles (guildid, guildname, roleid, rolename) values (%s, %s, %s, %s);")
    params = (guildname, str(guildid), rolename, str(roleid))

    try:
        database_cursor.execute(role_insert_stmt, params)
        database.commit()
    except:
        print("couldnt add role")
    


def get_channels(database, guildname: str, guildid: int):
    """
    Returns all channels the bot should listening to for a specific guild.
    """
    pass


def add_channel(database, guildname: str, guildid: int, channelname: str, channelid: int):
    """
    Adds a discord channel to the database

    tablelayout is the following:
    channels(
        guildid,
        guildname,
        channelid,
        channelname
    )
    """
    database_cursor = database.cursor()

    channel_insert_stmt = ("insert into channel (guildid, guildname, channelid, channelname) values (%s, %s, %s, %s);")
    params = (guildname, str(guildid), str(channelid), str(channelname))

    try:
        database_cursor.execute(channel_insert_stmt, params)
        database.commit()
    except:
        print("couldnt add channel")

    pass

def add_picture(database, pichash:str, guildname:str, guildid:int, authorname:str, authorid:int, width:int, height:int, imagepath:str):
    """
    Adds the path of the picture saved on the harddrive to the databse and some metadata about it

    tablelayout is the following:
    pictable(
        pichash,
        guildname,
        guildid,
        authorname,
        authorid,
        date,
        width,
        height,
        picpath
    )
    """
    database_cursor = database.cursor()

    insert_statement = (
                'insert into pictable (pichash, guildname, guildid, authorname, authorid, date, width, height, picpath) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);')

    params = (pichash, str(guildname), str(guildid), str(authorname), str(authorid), str(datetime.today(
    ).strftime('%Y-%m-%d')), int(width), int(height), imagepath)
    try:
        database_cursor.execute(insert_statement, params)
        database.commit()
        print("SAVED")
    except:
        print("Picture already exists")
        return False

    return True