from data.sql.migrations.migration import Migration

drop_tables = """
DROP TABLE IF EXISTS listening_history;
DROP TABLE IF EXISTS listening_period;
"""


class RemoveListeningTables(Migration):
    def __init__(self):
        super().__init__("v14")

    def migrate(self, cursor):
        cursor.execute(drop_tables)

    def reverse(self, _):
        print('Cannot reverse this migration')


if __name__ == '__main__':
    RemoveListeningTables().perform_migration()
