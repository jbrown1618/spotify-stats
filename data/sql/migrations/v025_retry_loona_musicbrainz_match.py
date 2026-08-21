from data.sql.migrations.migration import Migration


retry_loona_musicbrainz_match = """
DELETE FROM sp_artist_mb_artist
WHERE spotify_artist_uri = 'spotify:artist:52zMTJCKluDlFwMQWmccY7'
    AND artist_mbid = 'cb525a30-b590-448f-b94d-fab86e0e8756';

DELETE FROM mb_unmatchable_artist
WHERE artist_uri = 'spotify:artist:52zMTJCKluDlFwMQWmccY7';
"""


class RetryLoonaMusicBrainzMatch(Migration):
    def __init__(self):
        super().__init__("v25")

    def migrate(self, cursor):
        cursor.execute(retry_loona_musicbrainz_match)

    def reverse(self, cursor):
        pass


if __name__ == "__main__":
    RetryLoonaMusicBrainzMatch().perform_migration()
