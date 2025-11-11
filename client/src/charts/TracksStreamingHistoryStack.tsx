import { useState } from "react";

import { Track } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedTracks } from "../sorting";
import { useTracksCount, useTracksStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function TracksStreamingHistoryStack() {
  const [n, setN] = useState(5);
  const { data: trackCount } = useTracksCount();
  const {
    data: streamsByMonth,
    tracks,
    shouldRender,
  } = useTracksStreamsByMonth(n);

  if (!shouldRender) return null;

  if (!streamsByMonth || !tracks) return <ChartSkeleton />;

  return (
    <>
      <h3>Track streams by month</h3>
      <StreamingHistoryStack
        data={streamsByMonth}
        getItem={(key) => tracks[key]}
        sortItems={mostStreamedTracks}
        onMore={
          n < (trackCount ?? 0) ? () => setN((prev) => prev + 5) : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
        renderItem={(track: Track) => (
          <h4
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              margin: 0,
              whiteSpace: "nowrap",
            }}
          >
            <img height={20} src={track.album_image_url} />
            {track.track_name}
          </h4>
        )}
      />
    </>
  );
}
