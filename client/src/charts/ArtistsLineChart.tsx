import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamingHistory } from "../useApi";
import { RankLineChart } from "./RankLineChart";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistsRankLineChart({ height }: { height?: number }) {
  const { data: artists } = useArtists();
  const topArtistURIs = artists
    ? Object.values(artists)
        .sort(mostStreamedArtists)
        .slice(0, 10)
        .map((a) => a.artist_uri)
    : [];
  const { data: history } = useArtistsStreamingHistory(topArtistURIs);

  if (!history || !artists) return <ChartSkeleton />;

  return (
    <>
      <h3>Artist ranking over time</h3>
      <RankLineChart
        height={height}
        ranks={history}
        getKey={(r) => r.artist_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.artist_uri}
        getRank={(r) => r.artist_rank}
        getLabel={(k) => artists[k]?.artist_name}
        getCurrentRank={(k) => artists[k]?.artist_rank}
        getImageURL={(k) => artists[k]?.artist_image_url}
      />
    </>
  );
}

export function ArtistStreamsLineChart({ height }: { height?: number }) {
  const { data: artists } = useArtists();
  const topArtistURIs = artists
    ? Object.values(artists)
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
        getCurrentRank={(k) => artists[k]?.artist_rank}
        getImageURL={(k) => artists[k]?.artist_image_url}
      />
    </>
  );
}
