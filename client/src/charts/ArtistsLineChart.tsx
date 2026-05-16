import { ChartSkeleton } from "../design/ChartSkeleton";
import { useArtistsStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistStreamsLineChart({
  height,
  onlyArtist,
}: {
  height?: number;
  onlyArtist?: string;
}) {
  const { data: history, shouldRender } = useArtistsStreamingHistory();

  if (!shouldRender) return null;

  if (!history) return <ChartSkeleton />;

  const data = onlyArtist
    ? history.filter((h) => h.artist_uri === onlyArtist)
    : history;

  return (
    <>
      <h3>Artist streams over time</h3>
      <StreamsLineChart
        height={height}
        ranks={data}
        getKey={(r) => r.artist_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.artist_uri}
        getStreams={(r) => r.artist_stream_count}
        getLabel={(k) => history.find((r) => r.artist_uri === k)?.artist_name ?? k}
        getCurrentRank={(k) => (history.find((r) => r.artist_uri === k)?.artist_stream_count ?? 0) * -1}
        getImageURL={(k) => history.find((r) => r.artist_uri === k)?.artist_image_url ?? ""}
      />
    </>
  );
}
