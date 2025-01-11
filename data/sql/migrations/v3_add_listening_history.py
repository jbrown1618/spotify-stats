from data.sql.migrations.migration import Migration

add_listening_tables = """
CREATE TABLE listening_period (
    id SERIAL PRIMARY KEY,
    from_time TIMESTAMP NOT NULL,
    to_time TIMESTAMP NOT NULL,
    UNIQUE (from_time, to_time)
);

CREATE TABLE IF NOT EXISTS listening_history (
    id SERIAL PRIMARY KEY,
    listening_period_id INTEGER REFERENCES listening_period (id),
    track_uri TEXT NOT NULL,
    stream_count INTEGER DEFAULT 0,
    UNIQUE(listening_period_id, track_uri)
);
"""

remove_listening_tables = """
DROP TABLE IF EXISTS listening_period CASCADE;
DROP TABLE IF EXISTS listening_history CASCADE;
"""

class AddListeningHistory(Migration):
    def __init__(self):
        super().__init__("v3")

    def migrate(self, cursor):
        cursor.execute(remove_listening_tables)
        cursor.execute(add_listening_tables)


    def reverse(self, cursor):
        cursor.execute(remove_listening_tables)

if __name__ == '__main__':
    AddListeningHistory().reverse_migration()
    AddListeningHistory().perform_migration()
