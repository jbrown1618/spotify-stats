import spotipy
import pandas as pd
from data.raw import RawData, get_connection
from jobs.queue import queue_job
from spotify.spotify_client import get_spotify_client
from utils.name import short_name
from utils.track import is_blacklisted

page_size = 50
small_page_size = 20
max_playlist_track_change_ratio = 0.05

queued_artists = set()
queued_albums = set()

processed_playlists = set()
processed_tracks = set()
processed_albums = set()
processed_artists = set()

playlists_data = []
tracks_data = []
artists_data = []
albums_data = []

liked_tracks = []
playlist_track = []
track_artist = []
album_artist = []
artist_genre = []

def save_spotify_data():
    sp = get_spotify_client()
    save_playlists_data(sp)
    save_liked_tracks_data(sp)
    save_albums_data(sp)
    save_artists_data(sp)

    validate_playlist_track_count(len(playlist_track))

    raw_data = RawData()
    raw_data["playlists"] = pd.DataFrame(playlists_data)
    raw_data["tracks"] = pd.DataFrame(tracks_data)
    raw_data["artists"] = pd.DataFrame(artists_data)
    raw_data["albums"] = pd.DataFrame(albums_data)
    raw_data["liked_tracks"] = pd.DataFrame(liked_tracks)
    raw_data["playlist_track"] = pd.DataFrame(playlist_track)
    raw_data["track_artist"] = pd.DataFrame(track_artist)
    raw_data["album_artist"] = pd.DataFrame(album_artist)
    raw_data["artist_genre"] = pd.DataFrame(artist_genre)

    queue_job("standardize_record_labels")
    queue_job("repair_orphan_tracks")


def save_tracks_by_uri(uris):
    sp = get_spotify_client()
    while len(uris) > 0:
        print(f'Fetching {page_size} tracks...')

        uris_page = uris[0:page_size]
        uris = uris[page_size:]
        tracks = sp.tracks(uris_page)
        for track in tracks["tracks"]:
            process_track(track)
    save_albums_data(sp)
    save_artists_data(sp)

    raw_data = RawData()
    raw_data["tracks"] = pd.DataFrame(tracks_data)
    raw_data["artists"] = pd.DataFrame(artists_data)
    raw_data["albums"] = pd.DataFrame(albums_data)
    raw_data["track_artist"] = pd.DataFrame(track_artist)
    raw_data["album_artist"] = pd.DataFrame(album_artist)
    raw_data["artist_genre"] = pd.DataFrame(artist_genre)

def save_playlists_data(sp: spotipy.Spotify):
    offset = 0
    has_more = True
    while has_more:
        print(f'Fetching {page_size} current user playlists at offset {offset}...')
        playlists = sp.current_user_playlists(limit=page_size, offset=offset)
        log_playlist_page("current user playlists", playlists, offset)
        for playlist in playlists["items"]:
            if playlist is None:
                continue # This just started happening around 2024-11-28
            process_playlist(playlist)
            save_playlist_tracks_data(sp, playlist["uri"], playlist["name"])

        has_more = offset + page_size < playlists["total"]
        offset += page_size


def log_playlist_page(source: str, playlists: dict, offset: int):
    items = playlists["items"]
    null_count = sum(1 for playlist in items if playlist is None)
    names = [
        playlist["name"]
        for playlist in items
        if playlist is not None
    ]
    print(
        f'{source} offset={offset} total={playlists["total"]} '
        f'items={len(items)} null_items={null_count} playlists={names}'
    )


def save_playlist_tracks_data(sp: spotipy.Spotify, playlist_uri: str, playlist_name: str):
    offset = 0
    has_more = True
    page_count = 0
    spotify_total = 0
    saved_count = 0
    null_count = 0
    non_track_count = 0
    blacklisted_count = 0
    while has_more:
        print(f'Fetching {page_size} tracks for {playlist_name} at offset {offset}...')
        tracks = sp.playlist_tracks(playlist_uri, limit=page_size, offset=offset)
        page_count += 1
        spotify_total = tracks["total"]
        for item in tracks["items"]:
            track = item.get("track") if item is not None else None
            if track is None or track.get("type") != "track":
                if track is None:
                    null_count += 1
                else:
                    non_track_count += 1
                continue  # Skip episodes and other non-track items
            if is_blacklisted(track["name"]):
                blacklisted_count += 1
                continue  # Skip blacklisted tracks
            playlist_track.append({ "playlist_uri": playlist_uri, "track_uri": track["uri"] })
            process_track(track)
            saved_count += 1

        has_more = offset + page_size < tracks["total"]
        offset += page_size

    print(
        f'Playlist track sync summary: playlist="{playlist_name}" uri={playlist_uri} '
        f'spotify_total={spotify_total} pages={page_count} saved={saved_count} '
        f'null_items={null_count} non_track_items={non_track_count} '
        f'blacklisted={blacklisted_count}'
    )


def validate_playlist_track_count(new_count: int):
    existing_count = current_playlist_track_count()
    print(
        f'Playlist track sanity check: existing={existing_count} '
        f'fetched={new_count} max_decrease={max_playlist_track_change_ratio:.0%}'
    )

    if existing_count == 0:
        print('Skipping playlist track sanity check because the database has no existing rows.')
        return

    if new_count >= existing_count:
        return

    decrease_ratio = (existing_count - new_count) / existing_count
    if decrease_ratio > max_playlist_track_change_ratio:
        raise RuntimeError(
            f'Spotify sync fetched {new_count} playlist_track rows, but the database '
            f'currently has {existing_count}. The {decrease_ratio:.1%} decrease exceeds '
            f'the {max_playlist_track_change_ratio:.0%} safety threshold, so the job '
            'is aborting before replacing playlist_track.'
        )


def current_playlist_track_count() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM playlist_track;')
        return cursor.fetchone()[0]


def process_playlist(playlist):
    if playlist["uri"] in processed_playlists:
        return

    playlists_data.append(playlist_data(playlist))
    processed_playlists.add(playlist["uri"])


def playlist_data(playlist):
    fields = ["name", "collaborative", "public", "uri"]
    data = {field: playlist[field] for field in fields}
    if playlist["images"] is not None and len(playlist["images"]) > 0:
        data["image_url"] = playlist["images"][0]["url"]

    data["owner"] = playlist["owner"]["id"]
    return data


def save_liked_tracks_data(sp: spotipy.Spotify):
    offset = 0
    has_more = True
    while has_more:
        print(f'Fetching {page_size} liked tracks...')
        saved_tracks = sp.current_user_saved_tracks(limit=page_size, offset=offset)

        for item in saved_tracks["items"]:
            track = item["track"]
            if track is None or track.get("type") != "track":
                continue  # Skip episodes and other non-track items
            if is_blacklisted(track["name"]):
                continue  # Skip blacklisted tracks
            liked_tracks.append({ "track_uri": track["uri"] })
            process_track(track)

        has_more = offset + page_size < saved_tracks["total"]
        offset += page_size


def process_track(track):
    if track["uri"] in processed_tracks:
        return

    tracks_data.append(track_data(track))
    processed_tracks.add(track["uri"])
    
    for i, artist in enumerate(track["artists"]):
        track_artist.append({ "track_uri": track["uri"], "artist_uri": artist["uri"], "artist_index": i })
        queue_artist(artist)
    
    album = track["album"]
    queue_album(album)


def track_data(track):
    fields = ["name", "popularity", "explicit", "duration_ms", "uri"]
    data = {field: track[field] for field in fields}
    data["album_uri"] = track["album"]["uri"]
    data["isrc"] = track["external_ids"].get("isrc", None)
    data["short_name"] = short_name(track['name'])

    return data


def save_albums_data(sp: spotipy.Spotify):
    queue = [album_uri for album_uri in queued_albums]
    while len(queue) > 0:
        next = queue[0:small_page_size]
        queue = queue[small_page_size:]

        print(f'Fetching {len(next)} album details...')
        albums = sp.albums(albums=next)
        for album in albums["albums"]:
            process_album(album)


def queue_album(album):
    if album["uri"] in queued_albums:
        return

    queued_albums.add(album["uri"])


def process_album(album):
    if album["uri"] in processed_albums:
        return

    albums_data.append(album_data(album))
    processed_albums.add(album["uri"])

    for artist in album["artists"]:
        album_artist.append({ "album_uri": album["uri"], "artist_uri": artist["uri"] })
        queue_artist(artist)


def album_data(album):
    fields = ["name", "album_type", "label", "popularity", "total_tracks", "release_date", "uri"]
    data = {field: album[field] for field in fields}

    if album["images"] is not None and len(album["images"]) > 0:
        data["image_url"] = album["images"][0]["url"]

    data["short_name"] = short_name(album['name'])

    return data


def save_artists_data(sp: spotipy.Spotify):
    queue = [artist_uri for artist_uri in queued_artists]
    while len(queue) > 0:
        next = queue[0:page_size]
        queue = queue[page_size:]

        print(f'Fetching {len(next)} artist details...')
        artists = sp.artists(artists=next)
        for artist in artists["artists"]:
            process_artist(artist)

            
def queue_artist(artist):
    if artist["uri"] in queued_artists:
        return

    queued_artists.add(artist["uri"])


def process_artist(artist):
    if artist["uri"] in processed_artists:
        return

    for genre in artist["genres"]:
        artist_genre.append({"artist_uri": artist["uri"], "genre": genre})

    artists_data.append(artist_data(artist))
    processed_artists.add(artist["uri"])


def artist_data(artist):
    fields = ["name", "uri", "popularity"]
    data = {field: artist[field] for field in fields}

    data["followers"] = artist["followers"]["total"]

    if artist["images"] is not None and len(artist["images"]) > 0:
        data["image_url"] = artist["images"][0]["url"]

    return data


if __name__ == '__main__':
    save_spotify_data()