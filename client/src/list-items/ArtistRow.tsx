import { Album, Artist } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useSetFilters } from "../useFilters";
import { useIsMobile } from "../useIsMobile";

interface ArtistTileProps {
  artist: Artist;
  album_by_artist: Record<string, string[]>;
  albums: Record<string, Album>;
  large?: boolean;
}

export function ArtistRow({
  artist,
  album_by_artist,
  albums,
}: ArtistTileProps) {
  const isMobile = useIsMobile();
  const setFilters = useSetFilters();
  const onClick = () =>
    setFilters({
      artists: [artist.artist_uri],
    });

  const artistAlbums = album_by_artist[artist.artist_uri].map(
    (uri) => albums[uri]
  );
  const highestRankedAlbum = artistAlbums.sort(
    (a, b) => b.album_stream_count - a.album_stream_count
  )[0];

  return (
    <RowDesign
      onClick={onClick}
      primaryText={artist.artist_name}
      src={artist.artist_image_url}
      secondarySrc={highestRankedAlbum?.album_image_url}
      stats={[
        { label: "Rank", value: artist.artist_rank },
        { label: "Streams", value: artist.artist_stream_count },
        isMobile
          ? null
          : { label: "Popularity", value: artist.artist_popularity },
        isMobile
          ? null
          : {
              label: "Liked Tracks",
              value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
            },
      ]}
    />
  );
}
