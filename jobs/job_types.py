from jobs.expire_stale_jobs import expire_stale_jobs
from jobs.save_listening_data import save_listening_data
from jobs.save_discogs_data import save_discogs_data
from jobs.save_spotify_data import save_spotify_data
from jobs.save_musicbrainz_data import save_musicbrainz_data
from jobs.repair_orphan_tracks import repair_orphan_tracks
from jobs.standardize_record_labels import standardize_record_labels


job_types = {
    "expire_stale_jobs": expire_stale_jobs,
    "save_spotify_data": save_spotify_data,
    "save_listening_data": save_listening_data,
    "save_musicbrainz_data": save_musicbrainz_data,
    "save_discogs_data": save_discogs_data,
    "repair_orphan_tracks": repair_orphan_tracks,
    "standardize_record_labels": standardize_record_labels,
}