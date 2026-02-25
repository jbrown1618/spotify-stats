from data.sql.migrations.migration import Migration

add_columns = """
ALTER TABLE track ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT current_timestamp;
ALTER TABLE album ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT current_timestamp;
ALTER TABLE artist ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT current_timestamp;
"""

remove_columns = """
ALTER TABLE track DROP COLUMN IF EXISTS last_updated;
ALTER TABLE album DROP COLUMN IF EXISTS last_updated;
ALTER TABLE artist DROP COLUMN IF EXISTS last_updated;
"""


class AddLastUpdated(Migration):
    def __init__(self):
        super().__init__("v16")

    def migrate(self, cursor):
        cursor.execute(add_columns)

    def reverse(self, cursor):
        cursor.execute(remove_columns)


if __name__ == '__main__':
    AddLastUpdated().perform_migration()
