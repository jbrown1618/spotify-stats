from jobs.save_listening_data import save_listening_data
from jobs.save_spotify_data import save_spotify_data
from jobs.save_supplemental_data import save_supplemental_data
from jobs.repair_orphan_tracks import repair_orphan_tracks
from jobs.standardize_record_labels import standardize_record_labels
from utils.ranking import ensure_ranks


job_types = {
    "save_spotify_data": save_spotify_data,
    "save_listening_data": save_listening_data,
    "save_supplemental_data": save_supplemental_data,
    "ensure_ranks": ensure_ranks,
    "repair_orphan_tracks": repair_orphan_tracks,
    "standardize_record_labels": standardize_record_labels,
}