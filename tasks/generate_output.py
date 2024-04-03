from data.provider import DataProvider
from summarize.pages.artist import make_artist_summary
from summarize.pages.genre import make_genre_summary
from summarize.pages.label import make_label_summary
from summarize.pages.playlist import make_playlist_summary
from summarize.pages.overview import make_overview
from summarize.pages.errors import make_errors
from summarize.pages.producer import make_producer_summary
from utils.path import clear_markdown
from utils.settings import should_clear_markdown, should_generate_page


def generate_output():
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
            make_artist_summary(artist['artist_uri'])

    if should_generate_page('label'):
        for standardized_label in dp.labels(with_page=True)['album_standardized_label']:
            make_label_summary(standardized_label, dp.tracks(label=standardized_label, owned=True))

    if should_generate_page('genre'):
        for genre in dp.genres(with_page=True):
            make_genre_summary(genre, dp.tracks(genre=genre, owned=True))

    if should_generate_page('producer'):
        for mbid in dp.mb_artists(with_page=True)['artist_mbid']:
            make_producer_summary(mbid)
