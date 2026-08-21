from data.sql.migrations.migration import Migration


retry_ambiguous_discogs_artists = """
DELETE FROM discogs_unmatchable_track dut
USING track_artist ta, discogs_unmatchable_artist dua
WHERE dut.spotify_track_uri = ta.track_uri
    AND ta.artist_index = 0
    AND dua.spotify_artist_uri = ta.artist_uri
    AND dut.reason LIKE 'Multiple exact artist results for % without unique release evidence'
    AND dua.reason LIKE 'Multiple exact artist results for % without unique release evidence';

DELETE FROM discogs_unmatchable_artist
WHERE reason LIKE 'Multiple exact artist results for % without unique release evidence';
"""


class RetryAmbiguousDiscogsArtists(Migration):
    def __init__(self):
        super().__init__("v24")

    def migrate(self, cursor):
        cursor.execute(retry_ambiguous_discogs_artists)

    def reverse(self, cursor):
        pass


if __name__ == "__main__":
    RetryAmbiguousDiscogsArtists().perform_migration()
