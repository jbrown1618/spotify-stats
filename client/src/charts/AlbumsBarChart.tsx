import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useAlbums } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function AlbumsBarChart() {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;
  const { items: albums, total } = useAlbums({ sort: "Most liked tracks", limit: maxCount });

  if (total < 3) return null;

  if (!albums) return <ChartSkeleton />;

  const height = 100 + 30 * Math.min(maxCount, albums.length);
  return (
    <>
      <h3>Albums by liked tracks</h3>
      <BarChart
        h={height}
        data={albums
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
