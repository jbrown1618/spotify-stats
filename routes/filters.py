from data.repository import DataRepository
from routes.utils import to_json


repository = DataRepository()


def filter_options_payload():
    options = repository.filter_options()
    playlists = options.playlists
    artists = options.artists
    albums = options.albums
    producers = options.producers
    labels = options.labels["standardized_label"].to_list()
    genres = options.genres["genre"].to_list()

    return {
        "artists": to_json(
            artists[["artist_uri", "artist_name"]],
            "artist_uri",
        ),
        "albums": to_json(albums[["album_uri", "album_name"]], "album_uri"),
        "playlists": to_json(
            playlists[["playlist_uri", "playlist_name"]],
            "playlist_uri",
        ),
        "producers": to_json(
            producers[["producer_name", "producer_key"]],
            "producer_key",
        ),
        "labels": labels,
        "genres": genres,
        "years": [year for year in albums["album_release_year"].unique()],
    }