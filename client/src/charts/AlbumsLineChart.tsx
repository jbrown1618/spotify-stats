import { Album, AlbumRank } from "../api";
import { RankLineChart } from "./RankLineChart";

export function AlbumsLineChart({
  height,
  ranks,
  albums,
}: {
  height?: number;
  ranks: AlbumRank[];
  albums: Record<string, Album>;
}) {
  return (
    <RankLineChart
      height={height}
      ranks={ranks}
      getKey={(r) => r.album_uri}
      getDate={(r) => r.as_of_date}
      getItem={(r) => r.album_uri}
      getRank={(r) => r.album_rank}
      getLabel={(k) => albums[k]?.album_short_name}
      getCurrentRank={(k) => albums[k]?.album_rank}
      getImageURL={(k) => albums[k]?.album_image_url}
    />
  );
}
