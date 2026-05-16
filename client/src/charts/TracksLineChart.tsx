import { ChartSkeleton } from "../design/ChartSkeleton";
import { useTracksStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function TrackStreamsLineChart({ height }: { height?: number }) {
  const { data: ranks, shouldRender } = useTracksStreamingHistory();

  if (!shouldRender) return null;

  if (!ranks) return <ChartSkeleton />;

  return (
    <>
      <h3>Track streams over time</h3>
      <StreamsLineChart
        height={height ?? 550}
        ranks={ranks}
        getKey={(r) => r.track_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.track_uri}
        getStreams={(r) => r.track_stream_count}
        getLabel={(k) => ranks.find((r) => r.track_uri === k)?.track_short_name ?? k}
        getCurrentRank={(k) => -1 * (ranks.find((r) => r.track_uri === k)?.track_stream_count ?? 0)}
        getImageURL={(k) => ranks.find((r) => r.track_uri === k)?.album_image_url ?? ""}
      />
    </>
  );
}
