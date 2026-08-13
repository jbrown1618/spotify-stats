from data.sql.migrations.migration import Migration


remove_uncorrelated_discogs_videos = """
DELETE FROM discogs_video
WHERE track_position IS NULL
    OR track_title IS NULL;

ALTER TABLE discogs_video
    ALTER COLUMN track_position SET NOT NULL,
    ALTER COLUMN track_title SET NOT NULL;
"""

allow_uncorrelated_discogs_videos = """
ALTER TABLE discogs_video
    ALTER COLUMN track_position DROP NOT NULL,
    ALTER COLUMN track_title DROP NOT NULL;
"""


class RemoveUncorrelatedDiscogsVideos(Migration):
    def __init__(self):
        super().__init__("v17")

    def migrate(self, cursor):
        cursor.execute(remove_uncorrelated_discogs_videos)

    def reverse(self, cursor):
        cursor.execute(allow_uncorrelated_discogs_videos)


if __name__ == '__main__':
    RemoveUncorrelatedDiscogsVideos().perform_migration()