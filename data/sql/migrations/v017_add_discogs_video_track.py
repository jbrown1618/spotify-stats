from data.sql.migrations.migration import Migration


add_video_track = """
ALTER TABLE discogs_video
    ADD COLUMN IF NOT EXISTS track_position TEXT,
    ADD COLUMN IF NOT EXISTS track_title TEXT;
"""

remove_video_track = """
ALTER TABLE discogs_video
    DROP COLUMN IF EXISTS track_position,
    DROP COLUMN IF EXISTS track_title;
"""


class AddDiscogsVideoTrack(Migration):
    def __init__(self):
        super().__init__("v17")

    def migrate(self, cursor):
        cursor.execute(add_video_track)

    def reverse(self, cursor):
        cursor.execute(remove_video_track)


if __name__ == '__main__':
    AddDiscogsVideoTrack().perform_migration()