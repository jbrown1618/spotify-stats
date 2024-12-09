from data.sql.migrations.migration import Migration

add_rank_tables = """
CREATE TABLE track_rank (
    id SERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);

CREATE TABLE artist_rank (
    id SERIAL PRIMARY KEY,
    artist_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);

CREATE TABLE album_rank (
    id SERIAL PRIMARY KEY,
    album_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);
"""

remove_rank_tables = """
DROP TABLE IF EXISTS track_rank;
DROP TABLE IF EXISTS artist_rank;
DROP TABLE IF EXISTS album_rank;
"""

class AddTrackRanks(Migration):
    def __init__(self):
        super().__init__("v2")

    def migrate(self, cursor):
        cursor.execute(add_rank_tables)

    def reverse(self, cursor):
        cursor.execute(remove_rank_tables)

if __name__ == '__main__':
    AddTrackRanks().perform_migration()