import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { AlbumTile } from "../list-items/AlbumTile";
import { useAlbums } from "../useApi";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { data: albums } = useAlbums({ albums: [albumURI] });

  if (!albums) return null; // TODO: skeleton

  const album = albums[albumURI];
  if (!album) return null;

  return (
    <>
      <h2>{album.album_name}</h2>

      <div style={{ display: "flex", justifyContent: "center" }}>
        <AlbumTile large album={album} />
      </div>
      <AlbumsStreamingHistoryStack />
      <AlbumStreamsLineChart height={300} />
    </>
  );
}
