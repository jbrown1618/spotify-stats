import { Track, TrackRank } from "../api";
import { RankLineChart } from "./RankLineChart";
import { StreamsLineChart } from "./StreamsLineChart";

export function TracksRankLineChart({
  ranks,
  tracks,
}: {
  ranks: TrackRank[];
  tracks: Record<string, Track>;
}) {
  return (
    <RankLineChart
      ranks={ranks}
      getKey={(r) => r.track_uri}
      getDate={(r) => r.as_of_date}
      getItem={(r) => r.track_uri}
      getRank={(r) => r.track_rank}
      getLabel={(k) => tracks[k]?.track_short_name}
      getCurrentRank={(k) => tracks[k]?.track_rank}
      getImageURL={(k) => tracks[k]?.album_image_url}
    />
  );
}

export function TrackStreamsLineChart({
  ranks,
  tracks,
}: {
  ranks: TrackRank[];
  tracks: Record<string, Track>;
}) {
  return (
    <StreamsLineChart
      height={550}
      ranks={ranks}
      getKey={(r) => r.track_uri}
      getDate={(r) => r.as_of_date}
      getItem={(r) => r.track_uri}
      getStreams={(r) => r.track_stream_count}
      getLabel={(k) => tracks[k]?.track_short_name}
      getCurrentRank={(k) => tracks[k]?.track_rank}
      getImageURL={(k) => tracks[k]?.album_image_url}
    />
  );
}
