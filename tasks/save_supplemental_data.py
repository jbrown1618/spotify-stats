import musicbrainzngs
import json

from utils.settings import musicbrainz_useragent, musicbrainz_version, musicbrainz_contact

out = {}

def save_supplemental_data():
    pass


def test_musicbrainz():
    musicbrainzngs.set_useragent(musicbrainz_useragent(), musicbrainz_version(), musicbrainz_contact())

    aespa_id = 'b51c672b-85e0-48fe-8648-470a2422229f'
    savage_release_group_id = 'd35ed94d-8134-40b3-989a-6d1c5af9657b'
    savage_release_id = 'df6eef84-dfc2-49c7-8c3c-c0f6982623cc'
    savage_recording_id = '4b0e4bc5-9db0-41f4-881e-927f9b3bdacc'
    savage_isrc="KRA302100326"
    ningning_id = 'f2be7907-4f89-487a-a6b8-4b1dd83ebcc4'
    yoo_young_jin_id = '84a1b776-8b7b-4516-b8c6-cd00abdbb0c5'

    artist_results = musicbrainzngs.search_artists('aespa')
    for artist in artist_results['artist-list']:
        output("Artist search result", artist)

    artist = musicbrainzngs.get_artist_by_id(aespa_id)
    output("Artist by id", artist)

    output("Release groups for artist", musicbrainzngs.browse_release_groups(artist=aespa_id))

    output("Releases for release group", musicbrainzngs.browse_releases(release_group=savage_release_group_id))

    output("Recordings for release", musicbrainzngs.browse_recordings(release=savage_release_id, includes=["isrcs"]))

    output("Artist for recording", musicbrainzngs.browse_artists(recording=savage_recording_id))

    output("Label for release", musicbrainzngs.browse_labels(release=savage_release_id))

    # Get credits for producers, writers, arrangers
    output("Credits for recording", musicbrainzngs.get_recording_by_id(savage_recording_id, includes=['artist-rels', 'work-rels', 'work-level-rels']))

    # Get group members!!! Potentially other things too
    output("Related artists", musicbrainzngs.get_artist_by_id(aespa_id, includes=['artist-rels']))

    # Fill out info for abbreviated metadata from relations
    output("Artist details", musicbrainzngs.get_artist_by_id(ningning_id))

    # Genres for a song
    output("Tags / genres for a recording", musicbrainzngs.get_recording_by_id(savage_recording_id, includes=['tags']))

    # Genres for an artist
    output("Tags / genres for an artist", musicbrainzngs.get_artist_by_id(aespa_id, includes=['tags']))

    # Track by ISRC
    output("Recording by ISRC", musicbrainzngs.get_recordings_by_isrc(savage_isrc))

    print(json.dumps(out, indent=4))


def output(label, data):
    out[label] = data