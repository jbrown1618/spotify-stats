import { Album } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedAlbums } from "../sorting";
import { useAlbums, useAlbumsStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function AlbumsStreamingHistoryStack() {
  const { data: albums } = useAlbums();
  const topAlbumURIs = albums
    ? Object.values(albums)
        .sort(mostStreamedAlbums)
        .slice(0, 5)
        .map((a) => a.album_uri)
    : [];
  const { data: history } = useAlbumsStreamsByMonth(topAlbumURIs);

  if (!albums || !history) return <ChartSkeleton />;
  return (
    <StreamingHistoryStack
      data={history}
      getItem={(key) => albums[key]}
      sortItems={(a, b) => b.album_stream_count - a.album_stream_count}
      renderItem={(album: Album) => (
        <h4
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            margin: 0,
            whiteSpace: "nowrap",
          }}
        >
          <img height={20} src={album.album_image_url} />
          {album.album_name}
        </h4>
      )}
    />
  );
}
