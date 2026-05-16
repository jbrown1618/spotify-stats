import { useState } from "react";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useAlbumsStreamsByMonth } from "../useApi";
import styles from "./StreamingHistoryItem.module.css";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function AlbumsStreamingHistoryStack() {
  const [n, setN] = useState(5);
  const { data: response, shouldRender } = useAlbumsStreamsByMonth(n);

  if (!response?.streams || !response?.metadata) return <ChartSkeleton />;

  if (!shouldRender) return null;

  const metadataCount = Object.keys(response.metadata).length;

  return (
    <>
      <h3>Album streams by month</h3>
      <StreamingHistoryStack
        data={response.streams}
        getItem={(key) => ({
          name: response.metadata[key]?.album_short_name ?? key,
          image_url: response.metadata[key]?.album_image_url ?? "",
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
