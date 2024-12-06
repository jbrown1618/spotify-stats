
from data.sql.migrations.v2_add_track_ranks import AddTrackRanks

migrations = [
    AddTrackRanks()
]

if __name__ == '__main__':
    for m in migrations:
        success = m.perform_migration()
        if not success:
            break