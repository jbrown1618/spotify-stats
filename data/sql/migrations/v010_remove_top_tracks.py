from data.sql.migrations.migration import Migration

drop_tables = """
DROP TABLE IF EXISTS top_track;
DROP TABLE IF EXISTS top_artist;
"""


class RemoveTopTracks(Migration):
    def __init__(self):
        super().__init__("v10")


    def migrate(self, cursor):
        cursor.execute(drop_tables)

    def reverse(self, _):
        print('Cannot reverse this migration')


if __name__ == '__main__':
    RemoveTopTracks().perform_migration()
