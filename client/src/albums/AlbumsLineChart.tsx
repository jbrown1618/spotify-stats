import { Album, AlbumRank } from "../api";
import { RankLineChart } from "../design/RankLineChart";

export function AlbumsLineChart({
  ranks,
  albums,
}: {
  ranks: AlbumRank[];
  albums: Record<string, Album>;
}) {
  return (
    <RankLineChart
      ranks={ranks}
      getKey={(r) => r.album_uri}
      getDate={(r) => r.as_of_date}
      getRank={(r) => r.album_rank}
      getLabel={(k) => albums[k]?.album_short_name}
      getCurrentRank={(k) => albums[k]?.album_rank}
      getImageURL={(k) => albums[k]?.album_image_url}
    />
  );
}
