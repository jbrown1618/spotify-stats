import { Paper } from "@mantine/core";
import { Artist } from "../api";
import { useSetFilters } from "../useSetFilters";

interface ArtistTileProps {
  artist: Artist;
}

export function ArtistTile({ artist }: ArtistTileProps) {
  const setFilters = useSetFilters();
  return (
    <Paper
      shadow="md"
      style={{ padding: 10, cursor: "pointer" }}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          artists: [artist.artist_uri],
        }))
      }
    >
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={artist.artist_image_url} />
        {artist.artist_name}
      </div>
    </Paper>
  );
}
