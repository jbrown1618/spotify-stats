import { AlbumsRankLineChart } from "../charts/AlbumsLineChart";
import { AlbumTile } from "../list-items/AlbumTile";
import { useAlbums } from "../useApi";
import { useIsMobile } from "../useIsMobile";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { data: albums } = useAlbums({ albums: [albumURI] });
  const isMobile = useIsMobile();

  if (!albums) return null; // TODO: skeleton

  const album = albums[albumURI];
  if (!album) return null;

  return (
    <>
      <h2>{album.album_name}</h2>
      <div
        style={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          justifyContent: "center",
          gap: 16,
        }}
      >
        <div
          style={{ flexGrow: 0, alignSelf: isMobile ? "center" : undefined }}
        >
          <AlbumTile large album={album} />
        </div>
        <div style={{ flexGrow: 1 }}>
          <h3>Rank over time</h3>
          <AlbumsRankLineChart height={300} />
        </div>
      </div>
    </>
  );
}
