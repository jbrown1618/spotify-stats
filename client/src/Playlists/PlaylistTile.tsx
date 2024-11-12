import { Paper } from "@mantine/core";
import { Playlist } from "../api";

interface PlaylistTileProps {
  playlist: Playlist;
}

export function PlaylistTile({ playlist }: PlaylistTileProps) {
  return (
    <Paper shadow="md" style={{ padding: 10 }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={playlist.playlist_image_url} />
        {playlist.playlist_name}
      </div>
    </Paper>
  );
}
