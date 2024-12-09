from data.sql.migrations.migration import Migration
from utils.ranking import populate_track_ranks, populate_artist_ranks, populate_album_ranks

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

fetch_dates = """
SELECT DISTINCT as_of_date FROM top_track;
"""

class AddTrackRanks(Migration):
    def __init__(self):
        super().__init__("v2")

    def migrate(self, cursor):
        cursor.execute(remove_rank_tables)
        cursor.execute(add_rank_tables)
        
        cursor.execute(fetch_dates)
        dates = [row[0] for row in cursor.fetchall()]

        for date in dates:
            print(f'Populating track ranks for {date}')
            cursor.execute(populate_track_ranks, {"as_of_date": date})

            print(f'Populating artist ranks for {date}')
            cursor.execute(populate_artist_ranks, {"as_of_date": date})

            print(f'Populating album ranks for {date}')
            cursor.execute(populate_album_ranks, {"as_of_date": date})


    def reverse(self, cursor):
        cursor.execute(remove_rank_tables)

if __name__ == '__main__':
    AddTrackRanks().perform_migration()