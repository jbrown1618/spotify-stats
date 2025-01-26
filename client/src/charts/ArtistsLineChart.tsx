import { Artist, ArtistRank } from "../api";
import { RankLineChart } from "./RankLineChart";
import { StreamsLineChart } from "./StreamsLineChart";

export function ArtistsRankLineChart({
  height,
  ranks,
  artists,
}: {
  height?: number;
  ranks: ArtistRank[];
  artists: Record<string, Artist>;
}) {
  return (
    <RankLineChart
      height={height}
      ranks={ranks}
      getKey={(r) => r.artist_uri}
      getDate={(r) => r.as_of_date}
      getItem={(r) => r.artist_uri}
      getRank={(r) => r.artist_rank}
      getLabel={(k) => artists[k]?.artist_name}
      getCurrentRank={(k) => artists[k]?.artist_rank}
      getImageURL={(k) => artists[k]?.artist_image_url}
    />
  );
}

export function ArtistStreamsLineChart({
  height,
  ranks,
  artists,
}: {
  height?: number;
  ranks: ArtistRank[];
  artists: Record<string, Artist>;
}) {
  return (
    <StreamsLineChart
      height={height}
      ranks={ranks}
      getKey={(r) => r.artist_uri}
      getDate={(r) => r.as_of_date}
      getItem={(r) => r.artist_uri}
      getStreams={(r) => r.artist_stream_count}
      getLabel={(k) => artists[k]?.artist_name}
      getCurrentRank={(k) => artists[k]?.artist_rank}
      getImageURL={(k) => artists[k]?.artist_image_url}
    />
  );
}
