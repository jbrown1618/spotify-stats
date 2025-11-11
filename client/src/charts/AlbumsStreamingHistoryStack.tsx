import { useState } from "react";

import { Album } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedAlbums } from "../sorting";
import { useAlbums, useAlbumsStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function AlbumsStreamingHistoryStack() {
  const [n, setN] = useState(5);
  const { data: albums } = useAlbums();
  const { data: history, shouldRender } = useAlbumsStreamsByMonth(n);

  if (!albums || !history) return <ChartSkeleton />;

  if (!shouldRender) return null;

  return (
    <>
      <h3>Album streams by month</h3>
      <StreamingHistoryStack
        data={history}
        getItem={(key) => albums[key]}
        sortItems={mostStreamedAlbums}
        onMore={
          n < Object.keys(albums).length
            ? () => setN((prev) => prev + 5)
            : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
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
            {album.album_short_name}
          </h4>
        )}
      />
    </>
  );
}
