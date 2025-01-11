from data.sql.migrations.migration import Migration

remove_stream_count_column = """
ALTER TABLE track_rank
DROP COLUMN stream_count;

ALTER TABLE artist_rank
DROP COLUMN stream_count;

ALTER TABLE album_rank
DROP COLUMN stream_count;
"""

add_stream_count_column = """
ALTER TABLE track_rank
ADD stream_count INTEGER DEFAULT 0;

ALTER TABLE artist_rank
ADD stream_count INTEGER DEFAULT 0;

ALTER TABLE album_rank
ADD stream_count INTEGER DEFAULT 0;
"""

class AddStreamColumns(Migration):
    def __init__(self):
        super().__init__("v5")


    def migrate(self, cursor):
        cursor.execute(add_stream_count_column)


    def reverse(self, cursor):
        cursor.execute(remove_stream_count_column)


if __name__ == '__main__':
    AddStreamColumns().perform_migration()
