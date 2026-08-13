from data.sql.migrations.migration import Migration


remove_unmapped_discogs_tracks = """
DELETE FROM discogs_track dt
WHERE NOT EXISTS (
    SELECT 1
    FROM sp_track_discogs_track stdt
    WHERE stdt.discogs_master_id = dt.discogs_master_id
        AND stdt.discogs_track_position = dt.position
        AND stdt.discogs_track_title = dt.title
);
"""


class RemoveUnmappedDiscogsTracks(Migration):
    def __init__(self):
        super().__init__("v18")

    def migrate(self, cursor):
        cursor.execute(remove_unmapped_discogs_tracks)

    def reverse(self, cursor):
        pass


if __name__ == '__main__':
    RemoveUnmappedDiscogsTracks().perform_migration()