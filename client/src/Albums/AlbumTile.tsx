import { Paper } from "@mantine/core";
import { Album } from "../api";

interface AlbumTileProps {
  album: Album;
}

export function AlbumTile({ album }: AlbumTileProps) {
  return (
    <Paper shadow="md" style={{ padding: 10 }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <img src={album.album_image_url} />
        {album.album_name}
      </div>
    </Paper>
  );
}
