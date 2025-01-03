import { Album, Artist } from "../api";
import { LargeTileDesign } from "../design/LargeTileDesign";
import { TileDesign } from "../design/TileDesign";
import { useSetFilters } from "../useFilters";

interface ArtistTileProps {
  artist: Artist;
  albums_by_artist: Record<string, string[]>;
  albums: Record<string, Album>;
  large?: boolean;
}

export function ArtistTile({
  artist,
  albums_by_artist,
  albums,
  large,
}: ArtistTileProps) {
  const setFilters = useSetFilters();
  const onClick = () =>
    setFilters({
      artists: [artist.artist_uri],
    });

  if (!large)
    return (
      <TileDesign
        title={artist.artist_name}
        src={artist.artist_image_url}
        onClick={onClick}
      />
    );

  const artistAlbums = albums_by_artist[artist.artist_uri].map(
    (uri) => albums[uri]
  );
  const highestRankedAlbum = artistAlbums.sort(
    (a, b) => b.album_stream_count - a.album_stream_count
  )[0];

  return (
    <LargeTileDesign
      title={artist.artist_name}
      src={artist.artist_image_url}
      secondarySrc={highestRankedAlbum?.album_image_url}
      onClick={onClick}
      stats={[
        { label: "Rank", value: artist.artist_rank },
        { label: "Streams", value: artist.artist_stream_count },
        { label: "Popularity", value: artist.artist_popularity },
        {
          label: "Liked Tracks",
          value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
        },
        {
          label: "Albums",
          value: artistAlbums.length,
        },
      ]}
    />
  );
}
