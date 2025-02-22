from datetime import datetime
import pandas as pd
import musicbrainzngs as mb

from data.raw import RawData
from utils.settings import musicbrainz_max_tracks_per_run, musicbrainz_retry_days, musicbrainz_useragent, musicbrainz_version, musicbrainz_contact, musicbrainz_save_batch_size

recordings = []
credits = []
artists = []
artist_relationships = []
sp_track_recording = []
sp_artist_artist = []

unfetchable_isrcs = set()
unmatchable_artists = set()
artist_queue = set()
processed_artists = set()

def save_supplemental_data():
    global processed_artists
    global unfetchable_isrcs
    global unmatchable_artists

    raw = RawData()
    print('Saving supplemental data...')
    mb.set_useragent(musicbrainz_useragent(), musicbrainz_version(), musicbrainz_contact())

    if should_retry_unfetchable_data():
        raw['mb_unfetchable_isrcs'] = None
        raw['mb_unmatchable_artists'] = None

    all_tracks = raw['tracks']
    liked = raw['liked_tracks']
    track_recording = raw['sp_track_mb_recording']
    unfetchable_isrcs = set(raw['mb_unfetchable_isrcs']['isrc'])
    unmatchable_artists = set(raw['mb_unmatchable_artists']['artist_uri'])
    processed_artists = set(raw['mb_artists']['artist_mbid'])
    unfetched_tracks = all_tracks[
        all_tracks['track_uri'].isin(liked['track_uri']) &
        ~all_tracks['track_uri'].isin(track_recording['spotify_track_uri']) &
        ~all_tracks['track_isrc'].isin(unfetchable_isrcs)
    ]

    print(f'There are {len(unfetched_tracks)} unfetched ISRCs')

    i = 1
    for _, track in unfetched_tracks.iterrows():
        save_supplemental_data_for_isrc(track['track_isrc'], track['track_uri'])
        flush_artist_queue()
        i += 1
        if i % musicbrainz_save_batch_size() == 0:
            write_data()

        if i > musicbrainz_max_tracks_per_run():
            break
    
    search_for_additional_liked_artists()
    write_data()


def write_data():
    raw = RawData()
    if len(recordings) > 0:
        raw['mb_recordings'] = pd.DataFrame(recordings)

    if len(artists) > 0:
        raw['mb_artists'] = pd.DataFrame(artists)

    if len(credits) > 0:
        raw['mb_recording_credits'] = pd.DataFrame(credits)

    if len(artist_relationships) > 0:
        raw['mb_artist_relationships'] = pd.DataFrame(artist_relationships)

    if len(sp_track_recording) > 0:
        raw['sp_track_mb_recording'] = pd.DataFrame(sp_track_recording)

    if len(sp_artist_artist) > 0:
        raw['sp_artist_mb_artist'] = pd.DataFrame(sp_artist_artist)

    if len(unfetchable_isrcs) > 0:
        raw['mb_unfetchable_isrcs'] = pd.DataFrame({"isrc": [isrc for isrc in unfetchable_isrcs]})

    if len(unmatchable_artists) > 0:
        raw['mb_unmatchable_artists'] = pd.DataFrame({"artist_uri": [uri for uri in unmatchable_artists]})


def save_supplemental_data_for_isrc(isrc: str, spotify_uri: str):
    print(f'Fetching supplemental data for ISRC {isrc}')

    try:
        isrc_result = mb.get_recordings_by_isrc(isrc.upper())
    except:
        unfetchable_isrcs.add(isrc)
        return

    if len(isrc_result["isrc"]["recording-list"]) == 0:
        unfetchable_isrcs.add(isrc)
        return
    
    mbid = isrc_result["isrc"]["recording-list"][0]["id"]
    sp_track_recording.append({
        "spotify_track_uri": spotify_uri,
        "recording_mbid": mbid
    })

    recording = mb.get_recording_by_id(mbid, includes=[
        'artist-rels', 
        'work-rels', 
        'work-level-rels'
    ])["recording"]

    print(f"Found MBID {mbid} for ISRC {isrc} - {recording['title']}")

    primary_work = None
    for work_relation in recording.get("work-relation-list", []):
        # The recording is a performance of the song
        if work_relation['type'] == 'performance':
            primary_work = work_relation['work']
            break

    recordings.append({
        "recording_mbid": recording["id"],
        "recording_title": normalize_punctuation(recording["title"]),
        "recording_language": (primary_work or {}).get("language", None)
    })

    artist_relations = recording.get('artist-relation-list', []) + (primary_work or {}).get('artist-relation-list', [])
    for artist_relation in artist_relations:
        queue_artist(artist_relation['target'])

        if "assistant" in artist_relation.get('attribute-list', []):
            continue

        credit_type = standardize_credit_type(artist_relation['type'])
        if credit_type is None:
            continue

        credits.append({
            'recording_mbid': mbid,
            'artist_mbid': artist_relation['artist']['id'],
            'credit_type': credit_type,
            'credit_details': ';'.join(artist_relation.get('attribute-list', []))
        })


ignore_credit_types = {"conductor", "phonographic copyright", "misc", "audio", "creative direction"}
songwriter_aliases = {"composer", "writer"}
producer_aliases = {"programming", "recording", "producer", "editor", "mix", "engineer", "remixer"}
arranger_aliases = {"arranger", "instrument arranger", "vocal arranger", "orchestrator"}

def standardize_credit_type(credit_type):    
    if credit_type in ignore_credit_types:
        return None
    
    if credit_type in songwriter_aliases:
        return "songwriter"
    
    if credit_type in producer_aliases:
        return "producer"
    
    if credit_type in arranger_aliases:
        return "arranger"
    
    return credit_type


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
    artist = mb.get_artist_by_id(mbid, includes=['artist-rels', 'aliases'])['artist']
    print(f'Fetching supplemental data for artist {artist["name"]}')
    artists.append({
        "artist_mbid": mbid,
        "artist_mb_name": normalize_punctuation(artist["name"]),
        "artist_sort_name": normalize_punctuation(artist["sort-name"]),
        "artist_disambiguation": artist.get("disambiguation", None),
        "artist_type": artist.get("type", 'Unknown'),
        "artist_area": artist.get("area", {}).get("name", None),
        "artist_gender": artist.get("gender", None),
        "artist_birthplace": artist.get("begin-area", {}).get("name", None),
        "artist_start_date": artist.get("life-span", {}).get('begin', None),
        "artist_end_date": artist.get("life-span", {}).get('end', None)
    })

    sp_artists = RawData()['artists']
    matching_artists = sp_artists[sp_artists['artist_name'].apply(normalize_artist_name).isin({
        normalize_artist_name(artist['name']),
        normalize_artist_name(artist['sort-name'])
    })]
    if len(matching_artists) == 1:
        sp_artist_artist.append({
            "spotify_artist_uri": matching_artists.iloc[0]['artist_uri'],
            "artist_mbid": artist['id']
        })
    elif len(matching_artists) > 1:
        print(f'Found multiple artists matching {artist["name"]} - find a way to disambiguate')

    for artist_relation in artist.get('artist-relation-list', []):
        if not should_record_relationship(artist, artist_relation):
            continue

        other_mbid = artist_relation['artist']['id']
        artist_relationships.append({
            'artist_mbid': mbid if artist_relation['direction'] == 'forward' else other_mbid,
            'other_mbid': other_mbid if artist_relation['direction'] == 'forward' else mbid,
            'relationship_type': artist_relation['type']
        })
        queue_artist(other_mbid)


def should_record_relationship(artist, artist_relation):
    if artist_relation['type'] in {'artist rename', 'is person'}:
        return True
    
    # Fetch the members of a group
    if artist.get('type', 'Unknown').lower() == 'group' and artist_relation['type'] == 'member of band' and artist_relation['direction'] == 'backward':
        return True
    
    sp_artists = RawData()['artists']
    matching_artists = sp_artists[sp_artists['artist_name'] == artist_relation['artist']['name']]

    # For a subgroup or supergroup, fetch the details if it appears uniquely in my spotify
    if artist_relation['type'] == 'subgroup' and len(matching_artists) == 1:
        return True

    # For a group member, fetch the group they are part of if that group appears uniquely in my spotify
    if artist.get('type', 'Unknown').lower() == 'person' and artist_relation['type'] == 'member of band' and artist_relation['direction'] == 'forward' and len(matching_artists) == 1:
        return True
    
    return False

def search_for_additional_liked_artists():
    raw = RawData()
    liked = raw['liked_tracks']
    track_artist = raw['track_artist']
    artists = raw['artists']

    liked_tracks = pd.merge(liked, track_artist, on="track_uri")
    liked_artist_uris = pd.merge(liked_tracks, artists, on="artist_uri")['artist_uri'].unique()
    matched_artist_uris = raw['sp_artist_mb_artist']['spotify_artist_uri']
    artists_to_search = artists[
        artists['artist_uri'].isin(liked_artist_uris) & 
        ~(artists['artist_uri'].isin(matched_artist_uris)) &
        ~(artists['artist_uri'].isin(unmatchable_artists))
    ]

    for _, artist in artists_to_search.iterrows():
        results = mb.search_artists(artist['artist_name'], limit=2).get('artist-list', [])
        perfect_matches = [result for result in results if float(result.get('ext:score')) == 100]
        if len(perfect_matches) == 0:
            unmatchable_artists.add(artist['artist_uri'])
            print(f"No close matches for {artist['artist_name']}")
            continue
        
        if len(perfect_matches) > 1:
            unmatchable_artists.add(artist['artist_uri'])
            print(f"Multiple close matches for {artist['artist_name']}. Find a way to disambiguate.")
            continue

        print(f"Got an exact match for {artist['artist_name']}")
        sp_artist_artist.append({
            "spotify_artist_uri": artist['artist_uri'],
            "artist_mbid": results[0]['id']
        })
        queue_artist(results[0]['id'])

    flush_artist_queue()


replacements = {
    '-': {'\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2015'},
    "'": {'\u2018', '\u2019'},
    '"': {'\u201C', '\u201D'}
}

def normalize_punctuation(name: str):
    out = name
    for replacement, values in replacements.items():
        for value in values:
            out = out.replace(value, replacement)
    return out


def normalize_artist_name(name: str):
    return normalize_punctuation(name.strip().lower())


def should_retry_unfetchable_data() -> bool:
    day_of_year = datetime.now().timetuple().tm_yday
    retry_days = musicbrainz_retry_days()
    return (day_of_year % retry_days) <= 3