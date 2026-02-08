from data.sql.migrations.migration import Migration

drop_tables = """
DROP TABLE IF EXISTS track_rank;
DROP TABLE IF EXISTS album_rank;
DROP TABLE IF EXISTS artist_rank;
"""


class RemoveRankTables(Migration):
    def __init__(self):
        super().__init__("v15")

    def migrate(self, cursor):
        cursor.execute(drop_tables)

    def reverse(self, _):
        print('Cannot reverse this migration')


if __name__ == '__main__':
    RemoveRankTables().perform_migration()
