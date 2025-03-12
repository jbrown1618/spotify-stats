select distinct ag.genre
from artist_genre ag
where :filter_artists = false or ag.artist_uri in :artist_uris;