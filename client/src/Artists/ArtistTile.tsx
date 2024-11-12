import { Paper } from "@mantine/core";
import { Artist } from "../api";

interface ArtistTileProps {
  artist: Artist;
}

export function ArtistTile({ artist }: ArtistTileProps) {
  return (
    <Paper shadow="md" style={{ padding: 10 }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={artist.artist_image_url} />
        {artist.artist_name}
      </div>
    </Paper>
  );
}
