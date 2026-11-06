import { useState } from "react";

import { useArtistsCount, useArtistsStreamsByMonth } from "../useApi";
import { StreamingHistoryItem } from "./StreamingHistoryItem";
import { StreamingHistoryStack, StreamingHistoryStackSkeleton } from "./StreamingHistoryStack";
import { totalStreams } from "./utils";

export function ArtistsStreamingHistoryStack({
  onlyArtist,
}: {
  onlyArtist?: string;
}) {
  const [n, setN] = useState(5);
  const { data: artistCount } = useArtistsCount();
  const { data: response, shouldRender } = useArtistsStreamsByMonth(n);

  if (!response?.streams || !response?.metadata) return <StreamingHistoryStackSkeleton />;

  if (!shouldRender) return null;

  const streams = onlyArtist
    ? Object.fromEntries(
        Object.entries(response.streams).filter(
          ([artistUri]) => artistUri === onlyArtist
        )
      )
    : response.streams;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={streams}
        getItem={(key) => ({
          uri: key,
          name: response.metadata[key]?.artist_name ?? key,
          image_url: response.metadata[key]?.artist_image_url ?? "",
          stream_count: totalStreams(response.streams[key]),
        })}
        sortItems={(a, b) => b.stream_count - a.stream_count}
        onMore={
          n < (artistCount ?? 0)
            ? () => setN((prev) => prev + 5)
            : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
        renderItem={(item: { uri: string; name: string; image_url: string }) => (
          <StreamingHistoryItem
            filters={{ artists: [item.uri] }}
            imageUrl={item.image_url}
            name={item.name}
          />
        )}
      />
    </>
  );
}
