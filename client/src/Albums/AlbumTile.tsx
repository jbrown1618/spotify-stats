import { Paper } from "@mantine/core";
import { Album } from "../api";
import { useSetFilters } from "../useSetFilters";

interface AlbumTileProps {
  album: Album;
}

export function AlbumTile({ album }: AlbumTileProps) {
  const setFilters = useSetFilters();
  return (
    <Paper
      shadow="md"
      style={{ padding: 10, cursor: "pointer" }}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          albums: [album.album_uri],
        }))
      }
    >
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={album.album_image_url} />
        {album.album_name}
      </div>
    </Paper>
  );
}
