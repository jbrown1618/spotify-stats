import { ChartSkeleton } from "../design/ChartSkeleton";
import { useTracks, useTracksStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function TrackStreamsLineChart() {
  const { data: tracks } = useTracks();
  const { data: ranks, shouldRender } = useTracksStreamingHistory();

  if (!shouldRender) return null;

  if (!tracks || !ranks) return <ChartSkeleton />;

  return (
    <>
      <h3>Track streams over time</h3>
      <StreamsLineChart
        height={550}
        ranks={ranks}
        getKey={(r) => r.track_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.track_uri}
        getStreams={(r) => r.track_stream_count}
        getLabel={(k) => tracks[k]?.track_short_name}
        getCurrentRank={(k) => -1 * tracks[k].track_stream_count}
        getImageURL={(k) => tracks[k]?.album_image_url}
      />
    </>
  );
}
