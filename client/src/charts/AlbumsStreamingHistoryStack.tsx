import { useState } from "react";

import { useAlbumsCount, useAlbumsStreamsByMonth } from "../useApi";
import { StreamingHistoryItem } from "./StreamingHistoryItem";
import { StreamingHistoryStack, StreamingHistoryStackSkeleton } from "./StreamingHistoryStack";
import { totalStreams } from "./utils";

export function AlbumsStreamingHistoryStack() {
  const [n, setN] = useState(5);
  const { data: albumCount } = useAlbumsCount();
  const { data: response, shouldRender } = useAlbumsStreamsByMonth(n);

  if (!response?.streams || !response?.metadata) return <StreamingHistoryStackSkeleton />;

  if (!shouldRender) return null;

  return (
    <>
      <h3>Album streams by month</h3>
      <StreamingHistoryStack
        data={response.streams}
        getItem={(key) => ({
          uri: key,
          name: response.metadata[key]?.album_short_name ?? key,
          image_url: response.metadata[key]?.album_image_url ?? "",
          stream_count: totalStreams(response.streams[key]),
        })}
        sortItems={(a, b) => b.stream_count - a.stream_count}
        onMore={
          n < (albumCount ?? 0)
            ? () => setN((prev) => prev + 5)
            : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
        renderItem={(item: { uri: string; name: string; image_url: string }) => (
          <StreamingHistoryItem
            filters={{ albums: [item.uri] }}
            imageUrl={item.image_url}
            name={item.name}
          />
        )}
      />
    </>
  );
}
