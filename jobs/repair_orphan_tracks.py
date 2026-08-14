from data.repository import DataRepository


repository = DataRepository()


def repair_orphan_tracks():
    print('Identifying orphan tracks...')
    for orphan_uri, _ in repository.orphan_tracks():
        matching_track = repository.matching_track_for_orphan(orphan_uri)
        if matching_track is None:
            continue

        matching_uri, matching_name = matching_track
        print(f"Repairing '{matching_name}'...")
        repository.repair_orphan_track(orphan_uri, matching_uri)

    repository.delete_orphan_albums()
    repository.delete_orphan_artists()
    print('Done repairing orphan tracks')


if __name__ == '__main__':
    repair_orphan_tracks()