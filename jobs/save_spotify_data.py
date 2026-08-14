from dataclasses import dataclass, field
from typing import Any

import spotipy

from data.database import get_connection
from jobs.queue import queue_job
from spotify.spotify_client import get_spotify_client
from spotify.store import SpotifyStore
from utils.name import short_name
from utils.track import is_blacklisted


page_size = 50
small_page_size = 20


@dataclass
class SpotifyCollection:
    queued_artists: set[str] = field(default_factory=set)
    queued_albums: set[str] = field(default_factory=set)
    processed_playlists: set[str] = field(default_factory=set)
    processed_tracks: set[str] = field(default_factory=set)
    processed_albums: set[str] = field(default_factory=set)
    processed_artists: set[str] = field(default_factory=set)
    playlists: list[dict[str, Any]] = field(default_factory=list)
    tracks: list[dict[str, Any]] = field(default_factory=list)
    artists: list[dict[str, Any]] = field(default_factory=list)
    albums: list[dict[str, Any]] = field(default_factory=list)
    liked_tracks: list[dict[str, str]] = field(default_factory=list)
    playlist_tracks: list[dict[str, str]] = field(default_factory=list)
    track_artists: list[dict[str, Any]] = field(default_factory=list)
    album_artists: list[dict[str, str]] = field(default_factory=list)
    artist_genres: list[dict[str, str]] = field(default_factory=list)

    def collect_playlists(self, sp: spotipy.Spotify):
        offset = 0
        has_more = True
        while has_more:
            print(
                f"Fetching {page_size} current user playlists at offset {offset}..."
            )
            playlists = sp.current_user_playlists(limit=page_size, offset=offset)
            log_playlist_page("current user playlists", playlists, offset)
            for playlist in playlists["items"]:
                if playlist is None:
                    continue  # Spotify occasionally returns null playlist entries.
                self.process_playlist(playlist)
                self.collect_playlist_tracks(
                    sp,
                    playlist["uri"],
                    playlist["name"],
                )

            has_more = offset + page_size < playlists["total"]
            offset += page_size

    def collect_playlist_tracks(
        self,
        sp: spotipy.Spotify,
        playlist_uri: str,
        playlist_name: str,
    ):
        offset = 0
        has_more = True
        page_count = 0
        spotify_total = 0
        saved_count = 0
        null_count = 0
        non_track_count = 0
        blacklisted_count = 0
        while has_more:
            print(
                f"Fetching {page_size} tracks for {playlist_name} at offset {offset}..."
            )
            tracks = sp.playlist_tracks(
                playlist_uri,
                limit=page_size,
                offset=offset,
            )
            page_count += 1
            spotify_total = tracks["total"]
            for item in tracks["items"]:
                track = item.get("track") if item is not None else None
                if track is None or track.get("type") != "track":
                    if track is None:
                        null_count += 1
                    else:
                        non_track_count += 1
                    continue
                if is_blacklisted(track["name"]):
                    blacklisted_count += 1
                    continue
                self.playlist_tracks.append(
                    {
                        "playlist_uri": playlist_uri,
                        "track_uri": track["uri"],
                    }
                )
                self.process_track(track)
                saved_count += 1

            has_more = offset + page_size < tracks["total"]
            offset += page_size

        print(
            f'Playlist track sync summary: playlist="{playlist_name}" '
            f"uri={playlist_uri} spotify_total={spotify_total} pages={page_count} "
            f"saved={saved_count} null_items={null_count} "
            f"non_track_items={non_track_count} blacklisted={blacklisted_count}"
        )

    def collect_liked_tracks(self, sp: spotipy.Spotify):
        offset = 0
        has_more = True
        while has_more:
            print(f"Fetching {page_size} liked tracks...")
            saved_tracks = sp.current_user_saved_tracks(
                limit=page_size,
                offset=offset,
            )

            for item in saved_tracks["items"]:
                track = item["track"]
                if track is None or track.get("type") != "track":
                    continue
                if is_blacklisted(track["name"]):
                    continue
                self.liked_tracks.append({"track_uri": track["uri"]})
                self.process_track(track)

            has_more = offset + page_size < saved_tracks["total"]
            offset += page_size

    def collect_tracks_by_uri(self, sp: spotipy.Spotify, uris):
        remaining_uris = list(uris)
        while remaining_uris:
            uris_page = remaining_uris[:page_size]
            remaining_uris = remaining_uris[page_size:]
            print(f"Fetching {len(uris_page)} tracks...")
            tracks = sp.tracks(uris_page)
            for track in tracks["tracks"]:
                self.process_track(track)

    def collect_albums(self, sp: spotipy.Spotify):
        queue = list(self.queued_albums)
        while queue:
            next_page = queue[:small_page_size]
            queue = queue[small_page_size:]

            print(f"Fetching {len(next_page)} album details...")
            albums = sp.albums(albums=next_page)
            for album in albums["albums"]:
                self.process_album(album)

    def collect_artists(self, sp: spotipy.Spotify):
        queue = list(self.queued_artists)
        while queue:
            next_page = queue[:page_size]
            queue = queue[page_size:]

            print(f"Fetching {len(next_page)} artist details...")
            artists = sp.artists(artists=next_page)
            for artist in artists["artists"]:
                self.process_artist(artist)

    def process_playlist(self, playlist):
        if playlist["uri"] in self.processed_playlists:
            return

        self.playlists.append(playlist_data(playlist))
        self.processed_playlists.add(playlist["uri"])

    def process_track(self, track):
        if track["uri"] in self.processed_tracks:
            return

        self.tracks.append(track_data(track))
        self.processed_tracks.add(track["uri"])

        for index, artist in enumerate(track["artists"]):
            self.track_artists.append(
                {
                    "track_uri": track["uri"],
                    "artist_uri": artist["uri"],
                    "artist_index": index,
                }
            )
            self.queue_artist(artist)

        self.queue_album(track["album"])

    def process_album(self, album):
        if album["uri"] in self.processed_albums:
            return

        self.albums.append(album_data(album))
        self.processed_albums.add(album["uri"])

        for artist in album["artists"]:
            self.album_artists.append(
                {
                    "album_uri": album["uri"],
                    "artist_uri": artist["uri"],
                }
            )
            self.queue_artist(artist)

    def process_artist(self, artist):
        if artist["uri"] in self.processed_artists:
            return

        for genre in artist["genres"]:
            self.artist_genres.append(
                {
                    "artist_uri": artist["uri"],
                    "genre": genre,
                }
            )

        self.artists.append(artist_data(artist))
        self.processed_artists.add(artist["uri"])

    def queue_album(self, album):
        self.queued_albums.add(album["uri"])

    def queue_artist(self, artist):
        self.queued_artists.add(artist["uri"])


def save_spotify_data():
    sp = get_spotify_client()
    collection = SpotifyCollection()
    collection.collect_playlists(sp)
    collection.collect_liked_tracks(sp)
    collection.collect_albums(sp)
    collection.collect_artists(sp)

    save_collection(collection, replace_library=True)

    queue_job("standardize_record_labels")
    queue_job("repair_orphan_tracks")


def save_tracks_by_uri(uris):
    sp = get_spotify_client()
    collection = SpotifyCollection()
    collection.collect_tracks_by_uri(sp, uris)
    collection.collect_albums(sp)
    collection.collect_artists(sp)
    save_collection(collection, replace_library=False)


def save_collection(collection: SpotifyCollection, replace_library: bool):
    with get_connection() as conn:
        cursor = conn.cursor()
        store = SpotifyStore(cursor)
        store.save_playlists(collection.playlists)
        store.save_albums(collection.albums)
        store.save_artists(collection.artists)
        store.save_tracks(collection.tracks)
        store.save_track_artists(collection.track_artists)
        store.save_album_artists(collection.album_artists)
        store.save_artist_genres(collection.artist_genres)
        if replace_library:
            store.replace_liked_tracks(collection.liked_tracks)
            store.replace_playlist_tracks(collection.playlist_tracks)
        conn.commit()


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
        f"items={len(items)} null_items={null_count} playlists={names}"
    )


def playlist_data(playlist):
    fields = ["name", "collaborative", "public", "uri"]
    data = {field: playlist[field] for field in fields}
    if playlist["images"] is not None and len(playlist["images"]) > 0:
        data["image_url"] = playlist["images"][0]["url"]

    data["owner"] = playlist["owner"]["id"]
    return data


def track_data(track):
    fields = ["name", "popularity", "explicit", "duration_ms", "uri"]
    data = {field: track[field] for field in fields}
    data["album_uri"] = track["album"]["uri"]
    data["isrc"] = track["external_ids"].get("isrc", None)
    data["short_name"] = short_name(track["name"])
    return data


def album_data(album):
    fields = [
        "name",
        "album_type",
        "label",
        "popularity",
        "total_tracks",
        "release_date",
        "uri",
    ]
    data = {field: album[field] for field in fields}
    if album["images"] is not None and len(album["images"]) > 0:
        data["image_url"] = album["images"][0]["url"]
    data["short_name"] = short_name(album["name"])
    return data


def artist_data(artist):
    fields = ["name", "uri", "popularity"]
    data = {field: artist[field] for field in fields}
    data["followers"] = artist["followers"]["total"]
    if artist["images"] is not None and len(artist["images"]) > 0:
        data["image_url"] = artist["images"][0]["url"]
    return data


if __name__ == "__main__":
    save_spotify_data()
