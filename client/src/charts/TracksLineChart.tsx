import { ChartSkeleton } from "../design/ChartSkeleton";
import { useTracks, useTracksStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function TrackStreamsLineChart({ height }: { height?: number }) {
  const { items: tracks } = useTracks();
  const { data: ranks, shouldRender } = useTracksStreamingHistory();

  if (!shouldRender) return null;

  if (!tracks || !ranks) return <ChartSkeleton />;

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
        getLabel={(k) => tracks.find((t) => t.track_uri === k)?.track_short_name}
        getCurrentRank={(k) => -1 * (tracks.find((t) => t.track_uri === k)?.track_stream_count ?? 0)}
        getImageURL={(k) => tracks.find((t) => t.track_uri === k)?.album_image_url}
      />
    </>
  );
}
