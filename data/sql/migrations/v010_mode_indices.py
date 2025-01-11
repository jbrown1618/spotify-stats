from data.sql.migrations.migration import Migration

remove_indices = """
DROP INDEX IF EXISTS i_track_rank_as_of_date;
DROP INDEX IF EXISTS i_artist_rank_as_of_date;
DROP INDEX IF EXISTS i_album_rank_as_of_date;
DROP INDEX IF EXISTS i_track_artist_artist_uri_index;
"""

add_indices = """
CREATE INDEX IF NOT EXISTS i_track_rank_as_of_date ON track_rank(as_of_date);
CREATE INDEX IF NOT EXISTS i_artist_rank_as_of_date ON artist_rank(as_of_date);
CREATE INDEX IF NOT EXISTS i_album_rank_as_of_date ON album_rank(as_of_date);
CREATE INDEX IF NOT EXISTS i_track_artist_artist_uri_index ON track_artist(artist_uri, artist_index);
"""

class AddMoreIndices(Migration):
    def __init__(self):
        super().__init__("v10")


    def migrate(self, cursor):
        cursor.execute(add_indices)


    def reverse(self, cursor):
        cursor.execute(remove_indices)


if __name__ == '__main__':
    AddMoreIndices().reverse_migration()
    AddMoreIndices().perform_migration()
