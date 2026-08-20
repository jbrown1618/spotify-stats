from data.repository import DataRepository


repository = DataRepository()


def repair_orphan_tracks():
    print('Identifying orphan tracks...')
    orphan_tracks = repository.orphan_tracks()
    repaired_tracks = 0
    for orphan_uri, _ in orphan_tracks:
        matching_track = repository.matching_track_for_orphan(orphan_uri)
        if matching_track is None:
            continue

        matching_uri, matching_name = matching_track
        print(f"Repairing '{matching_name}'...")
        repaired_tracks += repository.repair_orphan_track(
            orphan_uri,
            matching_uri,
        )

    deleted_albums = repository.delete_orphan_albums()
    deleted_artists = repository.delete_orphan_artists()
    print('Done repairing orphan tracks')
    return {
        "orphan_tracks_found": len(orphan_tracks),
        "tracks_repaired": repaired_tracks,
        "orphan_albums_deleted": deleted_albums,
        "orphan_artists_deleted": deleted_artists,
    }


if __name__ == '__main__':
    repair_orphan_tracks()