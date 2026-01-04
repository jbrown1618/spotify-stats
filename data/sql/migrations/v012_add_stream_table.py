from data.sql.migrations.migration import Migration

create_stream_table = """
CREATE TABLE IF NOT EXISTS stream (
    id BIGSERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    played_at TIMESTAMP NOT NULL,
    UNIQUE(track_uri, played_at)
);
CREATE INDEX IF NOT EXISTS i_stream_track_uri ON stream (track_uri);
CREATE INDEX IF NOT EXISTS i_stream_played_at ON stream (played_at);
"""

drop_stream_table = """
DROP TABLE IF EXISTS stream;
"""


class AddStreamTable(Migration):
    def __init__(self):
        super().__init__("v12")

    def migrate(self, cursor):
        cursor.execute(create_stream_table)

    def reverse(self, cursor):
        cursor.execute(drop_stream_table)


if __name__ == '__main__':
    AddStreamTable().perform_migration()
