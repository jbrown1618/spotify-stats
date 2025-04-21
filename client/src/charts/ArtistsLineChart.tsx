import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamingHistory } from "../useApi";
import { useFilters } from "../useFilters";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistStreamsLineChart({ height }: { height?: number }) {
  const filters = useFilters();
  const { data: artists } = useArtists();
  const topArtistURIs = artists
    ? Object.values(artists)
        .filter(
          (a) =>
            filters.artists?.length != 1 || a.artist_uri === filters.artists[0]
        )
        .sort(mostStreamedArtists)
        .slice(0, 10)
        .map((a) => a.artist_uri)
    : [];
  const { data: history } = useArtistsStreamingHistory(topArtistURIs);

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
