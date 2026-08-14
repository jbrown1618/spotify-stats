from data.sql.migrations.migration import Migration


refactor_musicbrainz_ingestion = """
TRUNCATE
    sp_track_mb_recording,
    sp_artist_mb_artist,
    mb_recording_credit,
    mb_recording,
    mb_artist_relationship,
    mb_artist,
    mb_unfetchable_isrc,
    mb_unmatchable_artist;

ALTER TABLE mb_recording_credit
    DROP CONSTRAINT IF EXISTS mb_recording_credit_recording_mbid_artist_mbid_credit_type_key;
ALTER TABLE mb_recording_credit
    ADD COLUMN IF NOT EXISTS raw_role TEXT;
UPDATE mb_recording_credit SET raw_role = credit_type WHERE raw_role IS NULL;
ALTER TABLE mb_recording_credit ALTER COLUMN raw_role SET NOT NULL;
ALTER TABLE mb_recording_credit ALTER COLUMN credit_details SET DEFAULT '';
UPDATE mb_recording_credit SET credit_details = '' WHERE credit_details IS NULL;
ALTER TABLE mb_recording_credit ALTER COLUMN credit_details SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS i_mb_recording_credit_source_identity
    ON mb_recording_credit (recording_mbid, artist_mbid, raw_role, credit_details);

CREATE UNIQUE INDEX IF NOT EXISTS i_mb_artist_relationship_identity
    ON mb_artist_relationship (artist_mbid, other_mbid, relationship_type);

CREATE TABLE IF NOT EXISTS mb_artist_alias (
    artist_mbid TEXT NOT NULL,
    alias_name TEXT NOT NULL,
    sort_name TEXT NOT NULL DEFAULT '',
    locale TEXT NOT NULL DEFAULT '',
    alias_type TEXT NOT NULL DEFAULT '',
    primary_for_locale BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (artist_mbid, alias_name, sort_name, locale, alias_type)
);
CREATE INDEX IF NOT EXISTS i_mb_artist_alias_artist_mbid
    ON mb_artist_alias (artist_mbid);
CREATE INDEX IF NOT EXISTS i_mb_artist_alias_alias_name
    ON mb_artist_alias (LOWER(alias_name));

ALTER TABLE mb_unfetchable_isrc ADD COLUMN IF NOT EXISTS reason TEXT;
ALTER TABLE mb_unfetchable_isrc ADD COLUMN IF NOT EXISTS retry_after TIMESTAMP;
ALTER TABLE mb_unfetchable_isrc
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE mb_unmatchable_artist ADD COLUMN IF NOT EXISTS artist_name TEXT;
ALTER TABLE mb_unmatchable_artist ADD COLUMN IF NOT EXISTS reason TEXT;
ALTER TABLE mb_unmatchable_artist ADD COLUMN IF NOT EXISTS retry_after TIMESTAMP;
ALTER TABLE mb_unmatchable_artist
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
"""


reverse_musicbrainz_ingestion_refactor = """
DROP TABLE IF EXISTS mb_artist_alias;
DROP INDEX IF EXISTS i_mb_recording_credit_source_identity;
DROP INDEX IF EXISTS i_mb_artist_relationship_identity;
DELETE FROM mb_recording_credit duplicate
USING mb_recording_credit retained
WHERE duplicate.id > retained.id
    AND duplicate.recording_mbid = retained.recording_mbid
    AND duplicate.artist_mbid = retained.artist_mbid
    AND duplicate.credit_type = retained.credit_type;
ALTER TABLE mb_recording_credit DROP COLUMN IF EXISTS raw_role;
ALTER TABLE mb_recording_credit ALTER COLUMN credit_details DROP NOT NULL;
ALTER TABLE mb_recording_credit ALTER COLUMN credit_details DROP DEFAULT;
ALTER TABLE mb_recording_credit
    ADD CONSTRAINT mb_recording_credit_recording_mbid_artist_mbid_credit_type_key
    UNIQUE (recording_mbid, artist_mbid, credit_type);
ALTER TABLE mb_unfetchable_isrc DROP COLUMN IF EXISTS reason;
ALTER TABLE mb_unfetchable_isrc DROP COLUMN IF EXISTS retry_after;
ALTER TABLE mb_unfetchable_isrc DROP COLUMN IF EXISTS updated_at;
ALTER TABLE mb_unmatchable_artist DROP COLUMN IF EXISTS artist_name;
ALTER TABLE mb_unmatchable_artist DROP COLUMN IF EXISTS reason;
ALTER TABLE mb_unmatchable_artist DROP COLUMN IF EXISTS retry_after;
ALTER TABLE mb_unmatchable_artist DROP COLUMN IF EXISTS updated_at;
"""


class RefactorMusicBrainzIngestion(Migration):
    def __init__(self):
        super().__init__("v20")

    def migrate(self, cursor):
        cursor.execute(refactor_musicbrainz_ingestion)

    def reverse(self, cursor):
        cursor.execute(reverse_musicbrainz_ingestion_refactor)


if __name__ == "__main__":
    RefactorMusicBrainzIngestion().perform_migration()