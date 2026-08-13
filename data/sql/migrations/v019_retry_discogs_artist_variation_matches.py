from data.sql.migrations.migration import Migration


retry_discogs_artist_variation_matches = """
DELETE FROM discogs_unmatchable_track dut
USING track_artist ta, discogs_unmatchable_artist dua
WHERE dut.spotify_track_uri = ta.track_uri
    AND ta.artist_index = 0
    AND dua.spotify_artist_uri = ta.artist_uri
    AND dut.reason = 'No Discogs artist match'
    AND dua.reason = 'No exact Discogs artist match';

DELETE FROM discogs_unmatchable_artist
WHERE reason = 'No exact Discogs artist match';
"""


class RetryDiscogsArtistVariationMatches(Migration):
    def __init__(self):
        super().__init__("v19")

    def migrate(self, cursor):
        cursor.execute(retry_discogs_artist_variation_matches)

    def reverse(self, cursor):
        pass


if __name__ == '__main__':
    RetryDiscogsArtistVariationMatches().perform_migration()