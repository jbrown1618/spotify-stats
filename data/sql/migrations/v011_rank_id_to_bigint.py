from data.sql.migrations.migration import Migration
import sqlalchemy

migrate_to_bigint = """
-- Convert track_rank.id to BIGINT
ALTER TABLE track_rank ALTER COLUMN id SET DATA TYPE BIGINT;
ALTER SEQUENCE track_rank_id_seq AS BIGINT;

-- Convert album_rank.id to BIGINT
ALTER TABLE album_rank ALTER COLUMN id SET DATA TYPE BIGINT;
ALTER SEQUENCE album_rank_id_seq AS BIGINT;

-- Convert artist_rank.id to BIGINT
ALTER TABLE artist_rank ALTER COLUMN id SET DATA TYPE BIGINT;
ALTER SEQUENCE artist_rank_id_seq AS BIGINT;
"""

reverse_to_int = """
-- Convert track_rank.id back to INTEGER
ALTER SEQUENCE track_rank_id_seq AS INTEGER;
ALTER TABLE track_rank ALTER COLUMN id SET DATA TYPE INTEGER;

-- Convert album_rank.id back to INTEGER
ALTER SEQUENCE album_rank_id_seq AS INTEGER;
ALTER TABLE album_rank ALTER COLUMN id SET DATA TYPE INTEGER;

-- Convert artist_rank.id back to INTEGER
ALTER SEQUENCE artist_rank_id_seq AS INTEGER;
ALTER TABLE artist_rank ALTER COLUMN id SET DATA TYPE INTEGER;
"""


class RankIdToBigint(Migration):
    def __init__(self):
        super().__init__("v11")

    def migrate(self, conn):
        conn.execute(sqlalchemy.text(migrate_to_bigint))

    def reverse(self, conn):
        conn.execute(sqlalchemy.text(reverse_to_int))


if __name__ == '__main__':
    RankIdToBigint().perform_migration()
