import { Album, Artist } from "../api";
import { useSetFilters } from "../useSetFilters";
import { TileDesign } from "../design/TileDesign";
import { LargeTileDesign } from "../design/LargeTileDesign";

interface ArtistTileProps {
  artist: Artist;
  album_by_artist: Record<string, string[]>;
  albums: Record<string, Album>;
  large?: boolean;
}

export function ArtistTile({
  artist,
  album_by_artist,
  albums,
  large,
}: ArtistTileProps) {
  const setFilters = useSetFilters();
  const onClick = () =>
    setFilters((filters) => ({
      ...filters,
      artists: [artist.artist_uri],
    }));

  if (!large)
    return (
      <TileDesign
        title={artist.artist_name}
        src={artist.artist_image_url}
        onClick={onClick}
      />
    );

  const artistAlbums = album_by_artist[artist.artist_uri].map(
    (uri) => albums[uri]
  );
  const highestRankedAlbum = artistAlbums.sort(
    (a, b) => a.album_rank - b.album_rank
  )[0];

  return (
    <LargeTileDesign
      title={artist.artist_name}
      src={artist.artist_image_url}
      secondarySrc={highestRankedAlbum?.album_image_url}
      onClick={onClick}
      stats={[
        { label: "Rank", value: artist.artist_rank },
        { label: "Popularity", value: artist.artist_popularity },
        {
          label: "Liked Tracks",
          value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
        },
      ]}
    />
  );
}