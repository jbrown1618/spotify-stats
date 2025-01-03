import { AlbumsLineChart } from "../charts/AlbumsLineChart";
import { AlbumTile } from "../list-items/AlbumTile";
import { useSummary } from "../useSummary";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { data: summary } = useSummary();
  const album = summary?.albums[albumURI];
  if (!album) return null;

  return (
    <>
      <h2>{album.album_name}</h2>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-evenly",
          gap: 16,
        }}
      >
        <div style={{ flexGrow: 0 }}>
          <AlbumTile large album={album} />
        </div>
        <div
          style={{ flexGrow: 1, flexShrink: 1, minWidth: 100, maxWidth: 800 }}
        >
          <h3>Rank over time</h3>
          <AlbumsLineChart
            height={300}
            ranks={summary.album_rank_history.filter(
              (r) => r.album_uri === albumURI
            )}
            albums={summary.albums}
          />
        </div>
      </div>
    </>
  );
}
