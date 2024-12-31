from data.sql.migrations.migration import Migration

remove_indices = """
DROP INDEX IF EXISTS i_job_status_queue_time;
DROP INDEX IF EXISTS i_album_uri;
DROP INDEX IF EXISTS i_record_label_album_uri;
DROP INDEX IF EXISTS i_artist_uri;
DROP INDEX IF EXISTS i_track_uri;
DROP INDEX IF EXISTS i_playlist_uri;
DROP INDEX IF EXISTS i_liked_track_track_uri;
DROP INDEX IF EXISTS i_track_rank_track_uri;
DROP INDEX IF EXISTS i_artist_rank_artist_uri;
DROP INDEX IF EXISTS i_album_rank_album_uri;
DROP INDEX IF EXISTS i_album_artist_join;
DROP INDEX IF EXISTS i_artist_genre_join;
DROP INDEX IF EXISTS i_playlist_track_join;
DROP INDEX IF EXISTS i_track_artist_join;
DROP INDEX IF EXISTS i_track_artist_joinIndex;
"""

add_indices = """
CREATE INDEX IF NOT EXISTS i_job_status_queue_time ON job (status, queue_time);
CREATE INDEX IF NOT EXISTS i_album_uri ON album (uri);
CREATE INDEX IF NOT EXISTS i_record_label_album_uri ON record_label (album_uri);
CREATE INDEX IF NOT EXISTS i_artist_uri ON artist (uri);
CREATE INDEX IF NOT EXISTS i_track_uri ON track (uri);
CREATE INDEX IF NOT EXISTS i_playlist_uri ON playlist (uri);
CREATE INDEX IF NOT EXISTS i_liked_track_track_uri ON liked_track (track_uri);
CREATE INDEX IF NOT EXISTS i_track_rank_track_uri ON track_rank (track_uri);
CREATE INDEX IF NOT EXISTS i_artist_rank_artist_uri ON artist_rank (artist_uri);
CREATE INDEX IF NOT EXISTS i_album_rank_album_uri ON album_rank (album_uri);
CREATE INDEX IF NOT EXISTS i_album_artist_join ON album_artist (album_uri, artist_uri);
CREATE INDEX IF NOT EXISTS i_artist_genre_join ON artist_genre (artist_uri, genre);
CREATE INDEX IF NOT EXISTS i_playlist_track_join ON playlist_track (playlist_uri, track_uri);
CREATE INDEX IF NOT EXISTS i_track_artist_join ON track_artist (track_uri, artist_uri);
CREATE INDEX IF NOT EXISTS i_track_artist_joinIndex ON track_artist (track_uri, artist_uri, artist_index);
"""

class AddIndices(Migration):
    def __init__(self):
        super().__init__("v8")


    def migrate(self, cursor):
        cursor.execute(add_indices)


    def reverse(self, cursor):
        cursor.execute(remove_indices)


if __name__ == '__main__':
    AddIndices().reverse_migration()
    AddIndices().perform_migration()
