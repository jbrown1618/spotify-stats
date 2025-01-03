import { Track, TrackRank } from "../api";
import { RankLineChart } from "./RankLineChart";

export function TracksLineChart({
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
      getLabel={(k) => tracks[k]?.track_name}
      getCurrentRank={(k) => tracks[k]?.track_rank}
      getImageURL={(k) => tracks[k]?.album_image_url}
    />
  );
}
