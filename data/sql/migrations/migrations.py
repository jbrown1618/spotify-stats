
from data.sql.migrations.v002_add_track_ranks import AddTrackRanks
from data.sql.migrations.v003_add_listening_history import AddListeningHistory
from data.sql.migrations.v004_add_job import AddJobTable
from data.sql.migrations.v005_add_streams_to_rank import AddStreamColumns
from data.sql.migrations.v006_rank_additional_unique_constraint import AddRankURIConstraint
from data.sql.migrations.v007_add_standardized_label import AddLabelTable
from data.sql.migrations.v008_add_indices import AddIndices
from data.sql.migrations.v009_add_short_names import AddShortNames
from data.sql.migrations.v010_remove_top_tracks import RemoveTopTracks
from data.sql.migrations.v011_rank_id_to_bigint import RankIdToBigint
from data.sql.migrations.v012_add_stream_table import AddStreamTable
from data.sql.migrations.v013_remove_audio_features import RemoveAudioFeatures
from data.sql.migrations.v014_remove_listening_tables import RemoveListeningTables
from data.sql.migrations.v015_remove_rank_tables import RemoveRankTables

migrations = [
    AddTrackRanks(),
    AddListeningHistory(),
    AddJobTable(),
    AddStreamColumns(),
    AddRankURIConstraint(),
    AddLabelTable(),
    AddIndices(),
    AddShortNames(),
    RemoveTopTracks(),
    RankIdToBigint(),
    AddStreamTable(),
    RemoveAudioFeatures(),
    RemoveListeningTables(),
    RemoveRankTables()
]

def perform_all_migrations():
    for m in migrations:
        success = m.perform_migration()
        if not success:
            break

if __name__ == '__main__':
    perform_all_migrations()
