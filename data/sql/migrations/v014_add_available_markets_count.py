from data.sql.migrations.migration import Migration

add_column = """
ALTER TABLE track ADD COLUMN IF NOT EXISTS available_markets_count INT DEFAULT 0;
"""

drop_column = """
ALTER TABLE track DROP COLUMN IF EXISTS available_markets_count;
"""


class AddAvailableMarketsCount(Migration):
    def __init__(self):
        super().__init__("v14")


    def migrate(self, cursor):
        cursor.execute(add_column)

    def reverse(self, cursor):
        cursor.execute(drop_column)


if __name__ == '__main__':
    AddAvailableMarketsCount().perform_migration()
