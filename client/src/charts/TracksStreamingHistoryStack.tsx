import { useState } from "react";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useTracksCount, useTracksStreamsByMonth } from "../useApi";
import styles from "./StreamingHistoryItem.module.css";
import { StreamingHistoryStack } from "./StreamingHistoryStack";
import { totalStreams } from "./utils";

export function TracksStreamingHistoryStack() {
  const [n, setN] = useState(5);
  const { data: trackCount } = useTracksCount();
  const {
    data: response,
    shouldRender,
  } = useTracksStreamsByMonth(n);

  if (!shouldRender) return null;

  if (!response?.streams || !response?.metadata) return <ChartSkeleton />;

  return (
    <>
      <h3>Track streams by month</h3>
      <StreamingHistoryStack
        data={response.streams}
        getItem={(key) => ({
          name: response.metadata[key]?.track_name ?? key,
          image_url: response.metadata[key]?.album_image_url ?? "",
          stream_count: totalStreams(response.streams[key]),
        })}
        sortItems={(a, b) => b.stream_count - a.stream_count}
        onMore={
          n < (trackCount ?? 0) ? () => setN((prev) => prev + 5) : undefined
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
