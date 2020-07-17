import unittest
import sketbot.db.database_ops as do
import dotenv
import os


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        dotenv.load_dotenv()
        TOKEN = os.getenv("TOKEN")
        USERNAME = os.getenv("DB_USER")
        PW = os.getenv("DB_PW")
        PICTURE_FOLDER = os.getenv("PICTURE_FOLDER_PATH")

        self.database = do.open_database(
            "localhost", USERNAME, PW, "test_pictures")

        self.database.cursor().callproc("create_test_table")

    def tearDown(self):
        self.database.cursor().callproc("end_testing")
        self.database.close()


class GuildTest(DatabaseTest):
    def test_update(self):
        do.add_guild(self.database, "guildname1", 2194828943719823547)

        do.update_guild()


class GuildoptionsTest(DatabaseTest):
    def test_insert(self):
        do.add_guild(self.database, "guildname1", 2194828943719823547)
        do.add_guild(self.database, "deez nuts", 53429781423)

        # same name, but different ids
        do.add_guild(self.database, "funny", 123456789)
        do.add_guild(self.database, "funny", 987654321)

    def test_insert_duplicate(self):
        do.add_guild(self.database, "gn1", 123456789)
        with self.assertRaises(do.DatabaseException):
            do.add_guild(self.database, "gn1", 123456789)

    def test_insert_many(self):
        do.add_guild(self.database, [f"g{i}" for i in range(0, 1000)], [
                     i for i in range(0, 1000)])

        cursor = self.database.cursor()
        cursor.execute("select * from guildoptions;")

        items = []
        for item in cursor.fetchall():
            items.append(item)

        self.assertEqual(len(items), 1000)

    def test_update(self):
        do.add_guild(self.database, "guildname1", 2194828943719823547)
        do.add_guild(self.database, "deez nuts", 53429781423)

        do.update_guild_options(
            self.database, "guildname1", 2194828943719823547, crop_picture=True, safe_picture=True, random_icon_change=True, delete_interval=100)
        do.update_guild_options(
            self.database, "deez nuts", 53429781423, safe_picture=True, delete_interval=20)

        guild_options_1 = do.get_guild_options(
            self.database, "guildname1", 2194828943719823547)
        guild_options_2 = do.get_guild_options(
            self.database, "deez nuts", 53429781423)

        self.assertEqual(guild_options_1["crop_picture"], True)
        self.assertEqual(guild_options_1["safe_picture"], True)
        self.assertEqual(guild_options_1["random_icon_change"], True)
        self.assertEqual(guild_options_1["delete_interval"], 100)

        self.assertEqual(guild_options_2["crop_picture"], False)
        self.assertEqual(guild_options_2["safe_picture"], True)
        self.assertEqual(guild_options_2["random_icon_change"], False)
        self.assertEqual(guild_options_2["delete_interval"], 20)

    def test_remove(self):
        do.add_guild(self.database, "guildname1", 2194828943719823547)
        do.add_guild(self.database, "deez nuts", 53429781423)

        do.remove_guild(self.database, "guildname1", 2194828943719823547)

        with self.assertRaises(do.DatabaseException):
            do.get_guild_options(
                self.database, "guildname1", 2194828943719823547)


if __name__ == '__main__':
    unittest.main()
