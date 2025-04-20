
from data.sql.migrations.v002_add_track_ranks import AddTrackRanks
from data.sql.migrations.v003_add_listening_history import AddListeningHistory
from data.sql.migrations.v004_add_job import AddJobTable
from data.sql.migrations.v005_add_streams_to_rank import AddStreamColumns
from data.sql.migrations.v006_rank_additional_unique_constraint import AddRankURIConstraint
from data.sql.migrations.v007_add_standardized_label import AddLabelTable
from data.sql.migrations.v008_add_indices import AddIndices
from data.sql.migrations.v009_add_short_names import AddShortNames
from data.sql.migrations.v010_remove_top_tracks import RemoveTopTracks

migrations = [
    AddTrackRanks(),
    AddListeningHistory(),
    AddJobTable(),
    AddStreamColumns(),
    AddRankURIConstraint(),
    AddLabelTable(),
    AddIndices(),
    AddShortNames(),
    RemoveTopTracks()
]

def perform_all_migrations():
    for m in migrations:
        success = m.perform_migration()
        if not success:
            break

if __name__ == '__main__':
    perform_all_migrations()
