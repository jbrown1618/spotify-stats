import { useState } from "react";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useArtistsStreamsByMonth } from "../useApi";
import styles from "./StreamingHistoryItem.module.css";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function ArtistsStreamingHistoryStack({
  onlyArtist,
}: {
  onlyArtist?: string;
}) {
  const [n, setN] = useState(5);
  const { data: response, shouldRender } = useArtistsStreamsByMonth(n);

  if (!response?.streams || !response?.metadata) return <ChartSkeleton />;

  if (!shouldRender) return null;

  const streams = onlyArtist
    ? Object.fromEntries(
        Object.entries(response.streams).filter(
          ([artistUri]) => artistUri === onlyArtist
        )
      )
    : response.streams;

  const metadataCount = Object.keys(response.metadata).length;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={streams}
        getItem={(key) => ({
          name: response.metadata[key]?.artist_name ?? key,
          image_url: response.metadata[key]?.artist_image_url ?? "",
        })}
        sortItems={(a, b) => a.name.localeCompare(b.name)}
        onMore={
          n < metadataCount
            ? () => setN((prev) => prev + 5)
            : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
        renderItem={(item: { name: string; image_url: string }) => (
          <h4 className={styles.itemHeading}>
            <img className={styles.itemImage} src={item.image_url} />
            {item.name}
          </h4>
        )}
      />
    </>
  );
}
