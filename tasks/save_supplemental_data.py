import pandas as pd
import musicbrainzngs as mb

from data.raw import RawData
from utils.settings import musicbrainz_useragent, musicbrainz_version, musicbrainz_contact

recordings = []
credits = []
artists = []
artist_relationships = []
tags = []
sp_track_recording = []
sp_artist_artist = []

unfetchable_isrcs = set()
artist_queue = set()
processed_artists = set()

def save_supplemental_data():
    raw = RawData()
    print('Saving supplemental data...')
    mb.set_useragent(musicbrainz_useragent(), musicbrainz_version(), musicbrainz_contact())

    # all_tracks = RawData()['tracks']
    # try:
    #     track_recording = RawData()['sp_track_mb_recording']
    #     unfetched_isrcs = set(all_tracks[~all_tracks['track_id'].isin(track_recording['spotify_id'])])
    # except:
    #     unfetched_isrcs = set(all_tracks['isrc'])

    # print(f'There are {len(unfetched_isrcs)} unfetched ISRCs')

    save_supplemental_data_for_isrc("KRA302100326", "TODO")
    flush_artist_queue()
    
    raw['mb_recordings'] = pd.DataFrame(recordings)
    raw['mb_artists'] = pd.DataFrame(artists)
    raw['mb_recording_credits'] = pd.DataFrame(credits)
    raw['mb_artist_relationships'] = pd.DataFrame(artist_relationships)
    raw['mb_tags'] = pd.DataFrame(tags) # TODO: dedupe
    raw['sp_track_mb_recording'] = pd.DataFrame(sp_track_recording)
    raw['sp_artist_mb_artist'] = pd.DataFrame(sp_artist_artist)


def save_supplemental_data_for_isrc(isrc: str, spotify_uri: str):
    print(f'Fetching supplemental data for ISRC {isrc}')
    isrc_result = mb.get_recordings_by_isrc(isrc)
    if len(isrc_result["isrc"]["recording-list"]) == 0:
        unfetchable_isrcs.add(isrc)
        return
    
    mbid = isrc_result["isrc"]["recording-list"][0]["id"]
    sp_track_recording.append({
        "spotify_uri": spotify_uri,
        "mbid": mbid
    })
    print(f"Found MBID {mbid} for ISRC {isrc}")

    recording = mb.get_recording_by_id(mbid, includes=[
        'artist-rels', 
        'work-rels', 
        'work-level-rels', 
        'tags'
    ])["recording"]

    primary_work = None
    for work_relation in recording["work-relation-list"]:
        # The recording is a performance of the song
        if work_relation['type'] == 'performance':
            primary_work = work_relation['work']
            break

    recordings.append({
        "mbid": recording["id"],
        "title": recording["title"],
        "language": primary_work["language"] if primary_work is not None else None
    })

    artist_relations = recording['artist-relation-list'] + primary_work['artist-relation-list'] if primary_work is not None else recording['artist-relation-list']
    for artist_relation in artist_relations:
        queue_artist(artist_relation['target'])
        credits.append({
            'recording_mbid': mbid,
            'artist_mbid': artist_relation['artist']['id'],
            'credit_type': artist_relation['type']
        })

        # TODO
        sp_artist_artist.append({
            "spotify_uri": 'TODO',
            "mbid": artist_relation['artist']['id']
        })

    for tag in recording['tag-list']:
        tags.append({
            "tag": tag["name"],
            "entity_type": "recording",
            "mbid": mbid
        })


def queue_artist(mbid):
    if mbid in processed_artists:
        return
    artist_queue.add(mbid)


def flush_artist_queue():
    while len(artist_queue) > 0:
        for mbid in artist_queue.copy():
            processed_artists.add(mbid)
            save_supplemental_data_for_artist(mbid)
            artist_queue.remove(mbid)


def save_supplemental_data_for_artist(mbid):
    artist = mb.get_artist_by_id(mbid, includes=['artist-rels', 'tags'])['artist']
    artists.append({
        "mbid": mbid,
        "name": artist["name"],
        "sort_name": artist["sort-name"],
        "type": artist["type"],
        "area": artist.get("area", {}).get("name", None),
        "birthplace": artist.get("begin-area", {}).get("name", None),
        "start_date": artist.get("life-span", {}).get('begin', None),
        "end_date": artist.get("life-span", {}).get('end', None)
    })

    for tag in artist.get('tag-list', []):
        tags.append({
            "tag": tag["name"],
            "entity_type": "artist",
            "mbid": mbid
        })

    if artist['type'].lower() == 'group':
        for artist_relation in artist['artist-relation-list']:
            if artist_relation['type'] == 'member of band':
                other_mbid = artist_relation['artist']['id']
                artist_relationships.append({
                    'artist_mbid': mbid,
                    'other_mbid': other_mbid,
                    'relationship_type': artist_relation['type']
                })
                queue_artist(other_mbid)
            else:
                print(f'Unknown relationship type {artist_relation["type"]}')
