import { Album } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedAlbums } from "../sorting";
import { useAlbums, useAlbumsStreamsByMonth } from "../useApi";
import { useFilters } from "../useFilters";
import { countUniqueMonths } from "../utils";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function AlbumsStreamingHistoryStack() {
  const filters = useFilters();
  const { data: albums } = useAlbums();
  const topAlbumURIs = albums
    ? Object.values(albums)
        .filter(
          (a) =>
            filters.albums?.length != 1 || a.album_uri === filters.albums[0]
        )
        .sort(mostStreamedAlbums)
        .slice(0, 5)
        .map((a) => a.album_uri)
    : [];
  const { data: history } = useAlbumsStreamsByMonth(topAlbumURIs);

  if (!albums || !history) return <ChartSkeleton />;

  if (countUniqueMonths(history) < 3) return null;

  return (
    <>
      <h3>Album streams by month</h3>
      <StreamingHistoryStack
        data={history}
        getItem={(key) => albums[key]}
        sortItems={mostStreamedAlbums}
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
    </>
  );
}
