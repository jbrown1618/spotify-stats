import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedTracks } from "../sorting";
import { useTracks, useTracksStreamingHistory } from "../useApi";
import { RankLineChart } from "./RankLineChart";
import { StreamsLineChart } from "./StreamsLineChart";

export function TracksRankLineChart() {
  const { data: tracks } = useTracks();
  const topTenUris = Object.values(tracks ?? {})
    .sort(mostStreamedTracks)
    .slice(0, 10)
    .map((t) => t.track_uri);
  const { data: ranks } = useTracksStreamingHistory(topTenUris);

  if (!tracks || !ranks) return <ChartSkeleton />;

  const maxDate = Math.max(
    ...ranks.map((r) => new Date(r.as_of_date).getTime())
  );
  const currentRanks: Record<string, number> = {};
  for (const uri of topTenUris) {
    const currentRank =
      ranks.find(
        (r) =>
          r.track_uri === uri && new Date(r.as_of_date).getTime() === maxDate
      )?.track_rank ?? Number.MAX_SAFE_INTEGER;
    currentRanks[uri] = currentRank;
  }

  return (
    <>
      <h3>Track ranking over time</h3>
      <RankLineChart
        ranks={ranks}
        getKey={(r) => r.track_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.track_uri}
        getRank={(r) => r.track_rank}
        getLabel={(k) => tracks[k]?.track_short_name}
        getCurrentRank={(k) => currentRanks[k]}
        getImageURL={(k) => tracks[k]?.album_image_url}
      />
    </>
  );
}

export function TrackStreamsLineChart() {
  const { data: tracks } = useTracks();
  const topTenUris = Object.values(tracks ?? {})
    .sort(mostStreamedTracks)
    .slice(0, 10)
    .map((t) => t.track_uri);
  const { data: ranks } = useTracksStreamingHistory(topTenUris);

  if (!tracks || !ranks) return <ChartSkeleton />;

  const maxDate = Math.max(
    ...ranks.map((r) => new Date(r.as_of_date).getTime())
  );
  const currentRanks: Record<string, number> = {};
  for (const uri of topTenUris) {
    const currentRank =
      ranks.find(
        (r) =>
          r.track_uri === uri && new Date(r.as_of_date).getTime() === maxDate
      )?.track_rank ?? Number.MAX_SAFE_INTEGER;
    currentRanks[uri] = currentRank;
  }

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
        getCurrentRank={(k) => currentRanks[k]}
        getImageURL={(k) => tracks[k]?.album_image_url}
      />
    </>
  );
}
