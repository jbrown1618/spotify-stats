
from data.sql.migrations.v2_add_track_ranks import AddTrackRanks
from data.sql.migrations.v3_add_listening_history import AddListeningHistory
from data.sql.migrations.v4_add_job import AddJobTable
from data.sql.migrations.v5_add_streams_to_rank import AddStreamColumns
from data.sql.migrations.v6_rank_additional_unique_constraint import AddRankURIConstraint

migrations = [
    AddTrackRanks(),
    AddListeningHistory(),
    AddJobTable(),
    AddStreamColumns(),
    AddRankURIConstraint()
]

def perform_all_migrations():
    for m in migrations:
        success = m.perform_migration()
        if not success:
            break

if __name__ == '__main__':
    perform_all_migrations()
