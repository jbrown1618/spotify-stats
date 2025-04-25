import { Track } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedTracks } from "../sorting";
import { useTracksStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function TracksStreamingHistoryStack() {
  const {
    data: streamsByMonth,
    tracks,
    shouldRender,
  } = useTracksStreamsByMonth();

  if (!shouldRender) return null;

  if (!streamsByMonth || !tracks) return <ChartSkeleton />;

  return (
    <>
      <h3>Track streams by month</h3>
      <StreamingHistoryStack
        data={streamsByMonth}
        getItem={(key) => tracks[key]}
        sortItems={mostStreamedTracks}
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
