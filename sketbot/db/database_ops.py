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


def add_guild(database, guildname, guildid):
    """
    Add guild to guild table with options
    """
    cursor = database.cursor()

    insert_stmt_guild = ("""insert into guilds (guildid, guildname) values (%s, %s);""")

    insert_stmt_settings = ("""insert into guildoptions (guildid, crop_picture, safe_pictures, random_icon_change, delete_interval)
    values (%s, %s, %s, %s, %s);""")

    if isinstance(guildname, list) and isinstance(guildid, list):
        if len(guildname) != len(guildid):
            raise DatabaseException("Length of input lists arent equal")

        try:
            for guildname, guildid in zip(guildid, guildname):
                print(guildid, guildname)
                cursor.execute(insert_stmt_guild, (str(guildid), guildname))
                cursor.execute(insert_stmt_settings, (str(guildid), False, False, False, 0))
            database.commit()
        except mysql.connector.IntegrityError:
            #Duplicated entry
            pass
        except:
            raise DatabaseException("Insertion Error")

    elif isinstance(guildname, str) and isinstance(guildid, int):
        try:
            cursor.execute(insert_stmt_guild, (str(guildid), guildname))
            cursor.execute(insert_stmt_settings, (str(guildid), False, False, False, 0))
            database.commit()
        except mysql.connector.IntegrityError:
            #Duplicated entry
            pass
        except:
            raise DatabaseException("Insertion Error")
    else:
        raise DatabaseException("Type Error")


def update_guild(database, guildname_before: str, guildid_before: int, guildname_after: str, guildid_after: int):
    """
    Updates a guild if there were some changes on the discord guild
    """
    database_cursor = database.cursor()

    if guildname_after != guildname_before and guildid_before == guildid_after:
        database_cursor.execute("show tables;")
        for table in database_cursor.fetchall():
            update_guild_stmt = f"update {table[0]} set guildname=%s where guildid=%s and guildname=%s;"
            params = (guildname_after, str(guildid_before), guildname_before)
            try:
                database_cursor.execute(update_guild_stmt, params)
            # Database wont throw an error, when no item was found
            except:
                raise DatabaseException()
        try:
            database.commit()
        except:
            raise DatabaseException()
    else:
        raise DatabaseException("Guildid Error")


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


def update_guild_options(database, guildid: int, *, crop_picture: bool = None, safe_picture: bool = None, random_icon_change: bool = None, delete_interval: int = None):
    database_cursor = database.cursor()

    if crop_picture is not None:
        update_stmt = "update guildoptions set crop_picture=%s where guildid=%s and guildname=%s;"
        params = (crop_picture, str(guildid))
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    if safe_picture is not None:
        update_stmt = "update guildoptions set safe_pictures=%s where guildid=%s and guildname=%s;"
        params = (safe_picture, str(guildid))
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    if random_icon_change is not None:
        update_stmt = "update guildoptions set random_icon_change=%s where guildid=%s and guildname=%s;"
        params = (random_icon_change, str(guildid))
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    if delete_interval is not None:
        # TODO inrtoduce macros to determine minutes/hours/weeks
        if delete_interval == 0:
            pass
        elif delete_interval < 1:
            delete_interval = 1
        elif delete_interval > 168:
            delete_interval = 168  # 1 week

        update_stmt = "update guildoptions set delete_interval=%s where guildid=%s and guildname=%s;"
        params = (delete_interval, str(guildid))
        try:
            database_cursor.execute(update_stmt, params)
        except:
            raise DatabaseException()

    try:
        database.commit()
    except:
        raise DatabaseException()


def get_guild_options(database, guildname: str, guildid: int):
    """
    Returns guild options
    """
    database_cursor = database.cursor()

    get_options_stmt = "select crop_picture, safe_pictures, random_icon_change, delete_interval from guildoptions where guildname=%s and guildid=%s"
    params = (guildname, str(guildid))

    try:
        database_cursor.execute(get_options_stmt, params)
    except:
        raise DatabaseException("Error while receiving guild options")

    entry = database_cursor.fetchone()
    if entry is None:
        raise DatabaseException("Entry not found")

    crop_picture, safe_picture, random_icon_change, delete_interval = entry

    guild_options = {
        "crop_picture": bool(crop_picture), "safe_picture": bool(safe_picture), "random_icon_change": bool(random_icon_change), "delete_interval": delete_interval}

    return guild_options


def get_all_guilds(database):
    """
    returns a list of guilds the bot is active on
    """
    # This function isnt neccessary, because discord already provides this function
    pass


def add_role(database, guildid: int, rolename: str, roleid: int):
    """
    Adds a discord role to the database
    tablelayout is the following:
    """
    database_cursor = database.cursor()

    role_insert_stmt = "insert into roles (guildid, roleid, rolename) values (%s, %s, %s);"

    try:
        database_cursor.execute(role_insert_stmt, (str(guildid), rolename, str(roleid)))
        database.commit()
    except:
        raise DatabaseException()


def get_roles(database, guildname: str, guildid: int):
    """
    Returns all discord roles for a specific guild
    """
    database_cursor = database.cursor()
    role_get_stmt = "select roleid, rolename from roles where guildname=%s and guildid=%s"

    try:
        database_cursor.execute(role_get_stmt, (guildname, str(guildid)))
    except:
        raise DatabaseException()

    entries = database_cursor.fetchall()
    if entries is None or len(entries) == 0:
        raise DatabaseException("Entry not found")

    roles = []
    for roleid, rolename in entries:
        roles.append((roleid, rolename))

    return roles
    

def add_channel(database, guildid: int, channelname: str, channelid: int):
    """
    Adds a discord channel to the database
    """
    database_cursor = database.cursor()

    channel_insert_stmt = "insert into channels (guildid, channelid, channelname) values (%s, %s, %s);"

    try:
        database_cursor.execute(channel_insert_stmt, (str(guildid), str(channelid), channelname))
        database.commit()
    except:
        raise DatabaseException()


def get_channels(database, guildid: int):
    """
    Returns all channels the bot should listening to for a specific guild.
    """
    database_cursor = database.cursor()

    get_channels_stmt = "select channelid, channelname from channels where guildid=%s;"
    params = (str(guildid))

    try:
        database_cursor.execute(get_channels_stmt, params)
    except:
        raise DatabaseException()

    entries = database_cursor.fetchall()
    if entries is None or len(entries) == 0:
        raise DatabaseException("Entry not found")

    channels = []
    for channelid, channelname in database_cursor.fetchall():
        channels.append((channelid, channelname))

    return channels


def add_picture(database, pichash: str, guildid: int, authorname: str, authorid: int, width: int, height: int, imagepath: str):
    """
    Adds the path of the picture saved on the harddrive to the databse and some metadata about it
    """
    database_cursor = database.cursor()

    print(hash)

    insert_statement = (
        'insert into pictable (pichash, guildid, authorname, authorid, date, width, height, picpath) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);')

    params = (pichash, str(guildid), str(authorname), str(authorid), str(datetime.today(
    ).strftime('%Y-%m-%d')), int(width), int(height), imagepath)
    try:
        database_cursor.execute(insert_statement, params)
        database.commit()
        print("SAVED")
    except:
        raise DatabaseException()

    return True


def recover_from_database():
    # TODO
    pass


def recover_guild(database, guildname: str, guildid: int):
    database_cursor = database.cursor()

    get_guild_options_stmt = "select crop_picture, safe_pictures, random_icon_change from guildoptions where guildname=%s and guildid=%s"
    params = (guildname, guildid)

    guild_options = {}
    guild_channels = []
    guild_roles = []

    guild_channels = get_channels(database, guildname, guildid)
    guild_roles = get_roles(database, guildname, guildid)
    guild_options = get_guild_options(database, guildname, guildid)

    return guild_options, guild_channels, guild_roles
