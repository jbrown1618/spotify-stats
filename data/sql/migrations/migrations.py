
from data.sql.migrations.v2_add_track_ranks import AddTrackRanks
from data.sql.migrations.v3_add_job import AddJobTable

migrations = [
    AddTrackRanks(),
    AddJobTable()
]

def perform_all_migrations():
    for m in migrations:
        success = m.perform_migration()
        if not success:
            break

if __name__ == '__main__':
    perform_all_migrations()
