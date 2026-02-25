from data.sql.migrations.migration import Migration
import sqlalchemy

remove_constraints = """
ALTER TABLE track_rank
DROP CONSTRAINT unique_track_uri_as_of_date;

ALTER TABLE artist_rank
DROP CONSTRAINT unique_artist_uri_as_of_date;

ALTER TABLE album_rank
DROP CONSTRAINT unique_album_uri_as_of_date;
"""

add_constraints = """
ALTER TABLE track_rank
ADD CONSTRAINT unique_track_uri_as_of_date UNIQUE (track_uri, as_of_date);

ALTER TABLE artist_rank
ADD CONSTRAINT unique_artist_uri_as_of_date UNIQUE (artist_uri, as_of_date);

ALTER TABLE album_rank
ADD CONSTRAINT unique_album_uri_as_of_date UNIQUE (album_uri, as_of_date);
"""

class AddRankURIConstraint(Migration):
    def __init__(self):
        super().__init__("v6")


    def migrate(self, conn):
        conn.execute(sqlalchemy.text('''
        TRUNCATE track_rank;
        TRUNCATE album_rank;
        TRUNCATE artist_rank;
        '''))
        conn.execute(sqlalchemy.text(add_constraints))


    def reverse(self, conn):
        conn.execute(sqlalchemy.text(remove_constraints))


if __name__ == '__main__':
    AddRankURIConstraint().perform_migration()
