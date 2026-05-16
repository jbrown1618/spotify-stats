import { ChartSkeleton } from "../design/ChartSkeleton";
import { useAlbumsStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function AlbumStreamsLineChart({ height }: { height?: number }) {
  const { data: history, shouldRender } = useAlbumsStreamingHistory();

  if (!shouldRender) return null;

  if (!history) return <ChartSkeleton />;

  return (
    <>
      <h3>Album streams over time</h3>
      <StreamsLineChart
        height={height}
        ranks={history}
        getKey={(r) => r.album_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.album_uri}
        getStreams={(r) => r.album_stream_count}
        getLabel={(k) => history.find((r) => r.album_uri === k)?.album_short_name ?? k}
        getCurrentRank={(k) => ([...history].reverse().find((r) => r.album_uri === k)?.album_stream_count ?? 0) * -1}
        getImageURL={(k) => history.find((r) => r.album_uri === k)?.album_image_url ?? ""}
      />
    </>
  );
}
