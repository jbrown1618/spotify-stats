import { ChartSkeleton } from "../design/ChartSkeleton";
import { useArtists, useArtistsStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistStreamsLineChart({ height }: { height?: number }) {
  const { data: artists } = useArtists();
  const { data: history, shouldRender } = useArtistsStreamingHistory();

  if (!shouldRender) return null;

  if (!history || !artists) return <ChartSkeleton />;

  return (
    <>
      <h3>Artist streams over time</h3>
      <StreamsLineChart
        height={height}
        ranks={history}
        getKey={(r) => r.artist_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.artist_uri}
        getStreams={(r) => r.artist_stream_count}
        getLabel={(k) => artists[k]?.artist_name}
        getCurrentRank={(k) => artists[k]?.artist_stream_count * -1}
        getImageURL={(k) => artists[k]?.artist_image_url}
      />
    </>
  );
}
