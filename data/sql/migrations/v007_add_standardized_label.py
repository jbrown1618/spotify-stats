from data.sql.migrations.migration import Migration

remove_label_table = """
DROP TABLE IF EXISTS record_label;
"""

add_label_table = """
CREATE TABLE IF NOT EXISTS record_label (
    id SERIAL PRIMARY KEY,
    album_uri TEXT NOT NULL,
    standardized_label TEXT NOT NULL
);
"""

class AddLabelTable(Migration):
    def __init__(self):
        super().__init__("v7")


    def migrate(self, cursor):
        cursor.execute(remove_label_table)
        cursor.execute(add_label_table)


    def reverse(self, cursor):
        cursor.execute(remove_label_table)


if __name__ == '__main__':
    AddLabelTable().reverse_migration()
    AddLabelTable().perform_migration()
