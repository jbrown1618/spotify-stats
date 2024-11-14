import { Artist } from "./api";
import { useSetFilters } from "./useSetFilters";
import { TileDesign } from "./TileDesign";

interface ArtistTileProps {
  artist: Artist;
}

export function ArtistTile({ artist }: ArtistTileProps) {
  const setFilters = useSetFilters();
  return (
    <TileDesign
      title={artist.artist_name}
      src={artist.artist_image_url}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          artists: [artist.artist_uri],
        }))
      }
    />
  );
}
