import mysql.connector
from datetime import datetime

from sketbot.exception import DatabaseException


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

    tablelayout is the following:
    guildoptions(
        guildid varchar(100) not null,
        guildname varchar(100) not null,
        crop_picture boolean,
        safe_pictures boolean,
        random_icon_change boolean,
        primary key(guildid)
    );

    """
    database_cursor = database.cursor()

    insert_stmt = ("""insert into guildoptions (guildid, guildname, crop_picture, safe_pictures, random_icon_change)
    values (%s, %s, %s, %s, %s);""")
    params = (guildid, guildname, False, False, False)
    
    try:
        database_cursor.execute(insert_stmt, params)
        database.commit()
    except:
        raise DatabaseException()
    return True
        


def remove_guild(database, guildname: str, guildid: int):
    """
    remove everything from that guild in every table
    """
    database_cursor = database.cursor()

    database_cursor.execute("show tables;")
    for table in database_cursor.fetchall():
        remove_guild_stmt = f"delete from {table[0]} where guildname=%s and guildid=%s;"
        params = (guildname, str(guildid))

        try:
            database_cursor.execute(remove_guild_stmt, params)
        except:
            raise DatabaseException()
    try:
        database.commit()
    except:
        raise DatabaseException()


def update_guild(database, guildname_before: str, guildid_before: int, guildname_after: str, guildid_after: int):
    """
    Updates a guild if there were some changes on the discord guild
    """
    database_cursor = database.cursor()

    if guildname_after != guildid_before and guildid_before == guildid_after:
        database_cursor.execute("show tables;")
        for table in database_cursor.fetchall():
            update_guild_stmt = f"update {table[0]} set guildname=%s where guildid=%s and guildname=%s;"
            params = (guildname_after, str(guildid_before), guildname_before)
            try:
                database_cursor.execute(update_guild_stmt, params)
            #Database wont throw an error, when no item was found
            except:
                raise DatabaseException()
        try:
            database.commit()
        except:
            raise DatabaseException()

def update_guild_options(database, guildname: str, guildid: int,*, crop_picture: bool = None, safe_picture: bool = None, random_icon_change: bool = None):
    database_cursor = database.cursor()

    if crop_picture is not None:
        update_stmt = "update guildoptions set crop_picture=%s where guildid=%s and guildname=%s;"
        params = (crop_picture, safe_picture, random_icon_change, str(guildid), guildname)
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    if safe_picture is not None:
        update_stmt = "update guildoptions set safe_picture=%s where guildid=%s and guildname=%s;"
        params = (crop_picture, safe_picture, random_icon_change, str(guildid), guildname)
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    if random_icon_change is not None:
        update_stmt = "update guildoptions set random_icon_change=%s where guildid=%s and guildname=%s;"
        params = (crop_picture, safe_picture, random_icon_change, str(guildid), guildname)
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()
    
    try:
        database.commit()
    except:
        raise DatabaseException()


def get_all_guilds(database):
    """
    returns a list of guilds the bot is active on
    """
    #This function isnt neccessary, because discord already provides this function
    pass


def get_roles(database, guildname: str, guildid: int):
    """
    Returns all discord roles for a specific guild
    """
    database_cursor = database.cursor()
    role_get_stmt = "select roleid, rolename from roles where guildname=%s and guildid=%s"
    params = (guildname, str(guildid))

    try:
        database_cursor.execute(role_get_stmt, params)
    except:
        raise DatabaseException()

    roles = []
    for roleid, rolename in database_cursor.fetchall():
        roles.append((roleid, rolename))

    return roles


def add_role(database, guildname: str, guildid: int, rolename: str, roleid: int):
    """
    Adds a discord role to the database
    tablelayout is the following:
    roles(
        guildid,
        guildname,
        roleid,
        rolename
    )
    """
    database_cursor = database.cursor()

    role_insert_stmt = "insert into roles (guildid, guildname, roleid, rolename) values (%s, %s, %s, %s);"
    params = (guildname, str(guildid), rolename, str(roleid))

    try:
        database_cursor.execute(role_insert_stmt, params)
        database.commit()
    except:
        raise DatabaseException()
    return True
    


def get_channels(database, guildname: str, guildid: int):
    """
    Returns all channels the bot should listening to for a specific guild.
    """
    database_cursor = database.cursor()
    
    get_channels_stmt = "select channelid, channelname from channels where guildname=%s and guildid=%s;"
    params = (guildname, str(guildid))

    try:
        database_cursor.execute(get_channels_stmt, params)
    except:
        DatabaseException()

    channels = []
    for channelid, channelname in database_cursor.fetchall():
        channels.append((channelid, channelname))

    return channels


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

    channel_insert_stmt = "insert into channels (guildid, guildname, channelid, channelname) values (%s, %s, %s, %s);"
    params = (str(guildid), guildname,  str(channelid), channelname)

    try:
        database_cursor.execute(channel_insert_stmt, params)
        database.commit()
    except:
        raise DatabaseException()
        
    return True

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
        DatabaseException()

    return True

def recover_from_database():
    pass

def recover_guild(guildname:str, guildid:int):
    pass