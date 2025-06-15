import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostLikedAlbums } from "../sorting";
import { useAlbums } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function AlbumsBarChart() {
  const { data: albums } = useAlbums();
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  if (albums && Object.keys(albums).length < 3) return null;

  if (!albums) return <ChartSkeleton />;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(albums).length);
  return (
    <>
      <h3>Albums by liked tracks</h3>
      <BarChart
        h={height}
        data={Object.values(albums)
          .sort(mostLikedAlbums)
          .slice(0, maxCount)
          .map((p) => ({
            Artist: p.album_short_name,
            Liked: p.album_liked_track_count,
            Unliked: p.album_track_count - p.album_liked_track_count,
          }))}
        orientation="vertical"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        dataKey="Artist"
        type="stacked"
        withTooltip={!isMobile}
        withBarValueLabel={isMobile}
        withLegend
        legendProps={{ verticalAlign: "bottom" }}
        gridAxis="y"
      />
    </>
  );
}
