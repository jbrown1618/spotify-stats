from data.sql.migrations.migration import Migration


deduplicate_discogs_credits = """
WITH ranked_credits AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY
                discogs_master_id,
                track_position,
                COALESCE(discogs_artist_id, 0),
                artist_name,
                raw_role
            ORDER BY
                CASE source_type WHEN 'release' THEN 0 ELSE 1 END,
                id DESC
        ) AS duplicate_rank
    FROM discogs_credit
)
DELETE FROM discogs_credit
WHERE id IN (
    SELECT id
    FROM ranked_credits
    WHERE duplicate_rank > 1
);

CREATE UNIQUE INDEX IF NOT EXISTS i_discogs_credit_canonical_identity
    ON discogs_credit (
        discogs_master_id,
        track_position,
        COALESCE(discogs_artist_id, 0),
        artist_name,
        raw_role
    );
"""

allow_duplicate_discogs_credits = """
DROP INDEX IF EXISTS i_discogs_credit_canonical_identity;
"""


class DeduplicateDiscogsCredits(Migration):
    def __init__(self):
        super().__init__("v18")

    def migrate(self, cursor):
        cursor.execute(deduplicate_discogs_credits)

    def reverse(self, cursor):
        cursor.execute(allow_duplicate_discogs_credits)


if __name__ == '__main__':
    DeduplicateDiscogsCredits().perform_migration()