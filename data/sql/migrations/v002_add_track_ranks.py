from data.query import query_text
import sqlalchemy
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

fetch_dates = """
SELECT DISTINCT as_of_date FROM top_track;
"""

class AddTrackRanks(Migration):
    def __init__(self):
        super().__init__("v2")

    def migrate(self, conn):
        conn.execute(sqlalchemy.text(remove_rank_tables))
        conn.execute(sqlalchemy.text(add_rank_tables))
        
        dates = [row[0] for row in conn.execute(sqlalchemy.text(fetch_dates)).fetchall()]

        for date in dates:
            print(f'Populating track ranks for {date}')
            conn.execute(sqlalchemy.text(query_text('populate_track_ranks')), {"as_of_date": date})

            print(f'Populating artist ranks for {date}')
            conn.execute(sqlalchemy.text(query_text('populate_artist_ranks')), {"as_of_date": date})

            print(f'Populating album ranks for {date}')
            conn.execute(sqlalchemy.text(query_text('populate_album_ranks')), {"as_of_date": date})


    def reverse(self, conn):
        conn.execute(sqlalchemy.text(remove_rank_tables))


if __name__ == '__main__':
    AddTrackRanks().reverse_migration()
    AddTrackRanks().perform_migration()
