from typing import Optional
import pandas as pd
from data.provider import DataProvider
from summarize.figures.artist_rank_time_series import artist_rank_time_series
from summarize.figures.artist_top_tracks_time_series import artist_top_tracks_time_series
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.figures.top_albums_score_time_series import top_albums_score_time_series
from summarize.figures.top_tracks_score_time_series import top_tracks_score_time_series
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.producers_table import producers_table, production_credits_table
from summarize.tables.tracks_table import tracks_table
from utils.artist_relationship import mb_artist_display_name, relationship_description
from utils.markdown import md_summary_details, md_table, md_image, md_link, md_truncated_table
import utils.path as p
from utils.top_lists import get_term_length_phrase, graphable_top_list_terms_for_artists, top_list_terms


def make_artist_summary(artist_uri: str):
    dp = DataProvider()
    artist = dp.artist(artist_uri)
    artist_name = artist['artist_name']
    artist_image_url = artist['artist_image_url']

    print(f"Generating summary for artist {artist_name}")

    tracks = dp.tracks(artist_uris={artist_uri}, owned=True)
    playlists = dp.playlists(artist_uri=artist_uri)
    artist_genre = dp.artist_genre()

    content = []

    content += title(artist_name)
    content += image(artist_name, artist_image_url)
    if len(tracks) > 10:
        content += [md_link(f"See Track Features", p.artist_audio_features_path(artist_name, p.artist_path(artist_name))), ""]
        content += [md_link(f"See Clusters", p.artist_clusters_path(artist_name, p.artist_path(artist_name))), ""]
    content += relationships_section(artist_name, artist_uri)
    content += top_artists_rank_section(artist_name, artist_uri, artist['artist_rank'])
    content += top_tracks_section(artist_name, artist_uri)
    content += albums_section(artist_name, tracks)
    content += playlists_section(artist_name, artist_uri, playlists)
    content += labels_section(artist_name, tracks)
    content += genres_section(artist_name, artist_uri, artist_genre)
    content += credits_section(artist_name, artist_uri)
    content += producers_section(artist_name, artist_uri)
    content += tracks_section(artist_name, tracks)

    with open(p.artist_overview_path(artist_name), "w") as f:
        f.write("\n".join(content))

    if len(tracks) > 10:
        make_track_features_page(tracks, artist_name, p.artist_audio_features_path(artist_name), p.artist_audio_features_chart_path(artist_name))

    if len(tracks) > 50:
        make_clusters_page(tracks, artist_name, p.artist_clusters_path(artist_name), p.artist_clusters_figure_path(artist_name))


def title(artist_name):
    return ["", f"# {artist_name}", ""]


def image(artist_name, artist_image_url):
    return ["", md_image(artist_name, artist_image_url, 100), ""]


def relationships_section(artist_name, artist_uri):
    related_artists = DataProvider().related_artists(artist_uri)
    if related_artists is None or len(related_artists) == 0:
        return []

    phrases = [
        f'- {relationship_description(relationship, p.artist_path(artist_name))}'
        for _, relationship in related_artists.iterrows()
    ]

    return ["## Relationships", "", artist_name + ":"] + phrases + [""]


def top_artists_rank_section(artist_name, artist_uri, artist_rank):
    contents = []

    current_entries = DataProvider().top_artists(current=True, artist_uris=[artist_uri])

    if len(current_entries) > 0:
        rankings_list = [f'{artist_name} is currently:']
        for term in top_list_terms:
            entries_for_term = current_entries[current_entries['term'] == term]
            if len(entries_for_term) == 0:
                continue

            rank_for_term = entries_for_term['index'].iloc[0]
            if rank_for_term is None:
                continue
            
            rankings_list.append(f'- The #{rank_for_term} artist of {get_term_length_phrase(term)}')

        contents += rankings_list

    contents.append(f'- The #{int(artist_rank)} artist of {get_term_length_phrase("aggregate_score")}')
        
    time_series = artist_rank_time_series(
        artist_uri,
        artist_name,
        p.artist_rank_time_series_path(artist_name),
        p.artist_rank_time_series_path(artist_name, p.artist_path(artist_name))
    )

    if time_series is not None:
        contents += ["", time_series]

    if len(contents) == 0:
        return contents
    
    return ['## Artist Rank'] + contents


def top_tracks_section(artist_name, artist_uri):
    contents = []

    score_time_series = top_tracks_score_time_series(
        DataProvider().tracks(artist_uris={artist_uri}),
        p.artist_top_tracks_time_series_path(artist_name, 'score'),
        p.artist_top_tracks_time_series_path(artist_name, 'score', p.artist_path(artist_name))
    )

    if score_time_series != '':
        contents += ['', '### Top tracks of all time', '', score_time_series]

    for term in graphable_top_list_terms_for_artists:
        time_series_for_term = artist_top_tracks_time_series(
            artist_uri,
            term,
            p.artist_top_tracks_time_series_path(artist_name, term),
            p.artist_top_tracks_time_series_path(artist_name, term, p.artist_path(artist_name))
        )

        if time_series_for_term == '':
            continue

        contents += ['', md_summary_details(f'Top tracks of {get_term_length_phrase(term)} over time', time_series_for_term)]

    if len(contents) == 0:
        return contents
    
    return ['## Top Tracks', ''] + contents


def track_ranks_superlatives_list(
        track_name: str, 
        short_term_rank: Optional[int], 
        medium_term_rank: Optional[int], 
        long_term_rank: Optional[int], 
        on_repeat_rank: Optional[int]):
    
    number_of_superlatives = (0 if short_term_rank is None else 1) \
        + (0 if medium_term_rank is None else 1) \
        + (0 if long_term_rank is None else 1) \
        + (0 if on_repeat_rank is None else 1)
    
    if number_of_superlatives == 0:
        return []
    
    if number_of_superlatives == 1:
        if on_repeat_rank is not None:
            return [f'- {track_name} is the #{on_repeat_rank} track of {get_term_length_phrase("on_repeat")}']
        
        if short_term_rank is not None:
            return [f'- {track_name} is the #{short_term_rank} track of {get_term_length_phrase("short_term")}']
        
        if medium_term_rank is not None:
            return [f'- {track_name} is the #{medium_term_rank} track of {get_term_length_phrase("medium_term")}']
        
        if long_term_rank is not None:
            return [f'- {track_name} is the #{long_term_rank} track of {get_term_length_phrase("long_term")}']

    superlatives_list = [f'- {track_name} is:']

    if on_repeat_rank is not None:
        superlatives_list.append(f'    - the #{on_repeat_rank} track of {get_term_length_phrase("on_repeat")}')

    if short_term_rank is not None:
        superlatives_list.append(f'    - the #{short_term_rank} track of {get_term_length_phrase("short_term")}') 

    if medium_term_rank is not None:
        superlatives_list.append(f'    - the #{medium_term_rank} track of {get_term_length_phrase("medium_term")}') 

    if long_term_rank is not None:
        superlatives_list.append(f'    - the #{long_term_rank} track of {get_term_length_phrase("long_term")}') 

    return superlatives_list


def playlists_section(artist_name, artist_uri, playlists: pd.DataFrame):
    display_playlists = playlists.copy()
    display_playlists['playlist_artist_track_count'] = display_playlists['playlist_uri']\
        .apply(lambda playlist_uri: track_count_for_artist_in_playlist(playlist_uri, artist_uri))
    display_playlists = display_playlists.sort_values(by="playlist_artist_track_count", ascending=False)
    display_playlists["Art"] = display_playlists["playlist_image_url"]\
        .apply(lambda href: md_image("", href, 50))
    display_playlists["Playlist"] = display_playlists["playlist_uri"]\
        .apply(lambda uri: display_playlist(artist_name, uri, playlists))
    display_playlists["Tracks"] = display_playlists["playlist_artist_track_count"]
    display_playlists = display_playlists[["Art", "Tracks", "Playlist"]]

    return [
        '## Featured on Playlists',
        md_table(display_playlists),
        ''
    ]


def track_count_for_artist_in_playlist(playlist_uri: str, artist_uri: str) -> int:
    dp = DataProvider()
    tracks_for_artist_in_playlist = dp.tracks(playlist_uri=playlist_uri, artist_uris={artist_uri})
    return len(tracks_for_artist_in_playlist)


def albums_section(artist_name: str, artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return [
        "## Top Albums", 
        "", 
        top_albums_score_time_series(
            artist_tracks, 
            p.artist_top_albums_time_series_path(artist_name), 
            p.artist_top_albums_time_series_path(artist_name, p.artist_path(artist_name))
        ),
        "",
        md_truncated_table(table_data, 10, "See all albums"), 
        "",
    ]


def labels_section(artist_name: str, artist_tracks: pd.DataFrame):
    table_data = labels_table(artist_tracks, p.artist_path(artist_name))    
    return ["## Top Record Labels", "", md_table(table_data), ""]


def genres_section(artist_name, artist_uri, artist_genre: pd.DataFrame):
    genres_for_artist = artist_genre[artist_genre["artist_uri"] == artist_uri]

    if len(genres_for_artist) == 0:
        return []

    section = ["## Genres", ""]
    for i, g in genres_for_artist.iterrows():
        if g["genre_has_page"]:
            section.append(f"- {md_link(g['genre'], p.genre_overview_path(g['genre'], p.artist_path(artist_name)))}")
        else:
            section.append(f"- {g['genre']}")

    section.append("")
    return section


def credits_section(artist_name, artist_uri):
    out = []
    out += credit_types_subsection(artist_uri)
    out += member_credits_subsection(artist_name, artist_uri)
    out += production_credits_subsection(artist_name, artist_uri)

    if len(out) == 0:
        return []
    
    return ['## Credits', ''] + out


def credit_types_subsection(artist_uri):
    credits = DataProvider().track_credits(artist_uri=artist_uri, include_aliases=True)
    if len(credits) == 0:
        return []

    credits_by_type = credits.groupby("credit_type").agg({"recording_mbid": "count"}).reset_index()
    credits_by_type['credit_type'] = credits_by_type['credit_type'].apply(lambda t: t.capitalize())
    credits_by_type = credits_by_type.rename(columns={"credit_type": "Credit Type", "recording_mbid": "Tracks"})
    return [
        '### Credits by Type',
        '',
        md_table(credits_by_type),
        ''
    ]


def production_credits_subsection(artist_name, artist_uri):
    table = production_credits_table(artist_uri=artist_uri, relative_to=p.artist_overview_path(artist_name))

    if table is None:
        return []

    return [
        '### Production Credits',
        '',
        md_truncated_table(table),
        ''
    ]


def member_credits_subsection(artist_name, artist_uri):
    members = DataProvider().group_members(artist_uri)
    if members is None:
        return []
    
    credits = DataProvider().track_credits(artist_mbids=members["artist_mbid"], include_aliases=True)
    if len(credits) == 0:
        return []
    
    credits['display_name'] = credits.apply(lambda r: mb_artist_display_name(r, p.artist_path(artist_name)), axis=1)
    credits['credit_type'] = credits['credit_type'].apply(lambda t: t.capitalize())
    pivot = credits.pivot_table(
        values=['recording_mbid'], 
        index='credit_type', 
        columns='display_name', 
        aggfunc='count', 
        fill_value=0).reset_index()
    
    pivot.columns = [tup[1] for tup in pivot.columns]
    
    return [
        '### Member Credits', 
        "", 
        md_table(pivot)
    ]


def producers_section(artist_name, artist_uri):
    tracks = DataProvider().tracks(artist_uris={artist_uri}, owned=True)
    producers = producers_table(tracks, p.artist_path(artist_name))

    if len(producers) == 0:
        return []
    
    bar_chart = producers_bar_chart(
        tracks, 
        p.artist_producers_graph_path(artist_name),
        p.artist_producers_graph_path(artist_name, p.artist_path(artist_name)))
    
    return [
        '## Top Producers',
        '',
        md_truncated_table(producers),
        '',
        bar_chart
    ]


def tracks_section(artist_name: str, tracks: pd.DataFrame):
    display_tracks = tracks_table(tracks, p.artist_path(artist_name), sorting='default')
    return ["## Tracks", "", md_truncated_table(display_tracks, 10, "See all tracks"), ""]


def display_playlist(artist_name: str, playlist_uri: str, playlists: pd.DataFrame):
    playlist = playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]
    return md_link(playlist["playlist_name"], p.playlist_overview_path(playlist["playlist_name"], p.artist_path(artist_name)))
