select distinct rl.standardized_label
from record_label rl
where :filter_albums = false or rl.album_uri in :album_uris;