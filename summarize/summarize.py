from data.provider import DataProvider
from summarize.pages.artist import make_artist_summary
from summarize.pages.genre import make_genre_summary
from summarize.pages.label import make_label_summary
from summarize.pages.playlist import make_playlist_summary
from summarize.pages.overview import make_overview
from summarize.pages.errors import make_errors
from utils.path import clear_markdown
from utils.settings import should_clear_markdown, should_generate_page


def summarize_results():
    dp = DataProvider()

    if should_clear_markdown():
        clear_markdown()

    if should_generate_page('overview'):
        make_overview(dp.tracks())

    if should_generate_page('errors'):
        make_errors(dp.tracks(), dp.albums())

    if should_generate_page('playlist'):
        make_playlist_summary(None, dp.tracks(liked=True))

        for i, playlist in dp.playlists().iterrows():
            playlist_tracks = dp.tracks(playlist_uri=playlist['playlist_uri'])
            if len(playlist_tracks) == 0:
                continue

            make_playlist_summary(playlist['playlist_uri'], playlist_tracks)

    if should_generate_page('artist'):
        for _, artist in dp.artists(with_page=True).iterrows():
            artist_uri=artist['artist_uri']
            make_artist_summary(artist, dp.tracks(artist_uri=artist_uri), dp.playlists(artist_uri=artist_uri), dp.artist_genre())

    if should_generate_page('label'):
        for standardized_label in dp.labels(with_page=True)['album_standardized_label']:
            make_label_summary(standardized_label, dp.tracks(label=standardized_label))

    if should_generate_page('genre'):
        for genre in dp.genres(with_page=True):
            make_genre_summary(genre, dp.tracks(genre=genre))
