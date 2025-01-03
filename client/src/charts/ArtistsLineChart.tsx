import { Artist, ArtistRank } from "../api";
import { RankLineChart } from "./RankLineChart";

export function ArtistsLineChart({
  ranks,
  artists,
}: {
  ranks: ArtistRank[];
  artists: Record<string, Artist>;
}) {
  return (
    <RankLineChart
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
