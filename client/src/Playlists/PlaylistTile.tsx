import { Paper } from "@mantine/core";
import { Playlist } from "../api";
import { useSetFilters } from "../useSetFilters";

interface PlaylistTileProps {
  playlist: Playlist;
}

export function PlaylistTile({ playlist }: PlaylistTileProps) {
  const setFilters = useSetFilters();
  return (
    <Paper
      shadow="md"
      style={{ padding: 10, cursor: "pointer" }}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          playlists: [playlist.playlist_uri],
        }))
      }
    >
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={playlist.playlist_image_url} />
        {playlist.playlist_name}
      </div>
    </Paper>
  );
}
