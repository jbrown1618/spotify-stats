import { ChartSkeleton } from "../design/ChartSkeleton";
import { useArtists, useArtistsStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistStreamsLineChart({
  height,
  onlyArtist,
}: {
  height?: number;
  onlyArtist?: string;
}) {
  const { data: artists } = useArtists();
  const { data: history, shouldRender } = useArtistsStreamingHistory();

  if (!shouldRender) return null;

  if (!history || !artists) return <ChartSkeleton />;

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
        getLabel={(k) => artists[k]?.artist_name}
        getCurrentRank={(k) => artists[k]?.artist_stream_count * -1}
        getImageURL={(k) => artists[k]?.artist_image_url}
      />
    </>
  );
}
