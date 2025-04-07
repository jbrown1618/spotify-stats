import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useGenres } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function GenresBarChart() {
  const { data: genres } = useGenres();
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  if (!genres) return <ChartSkeleton />;

  const height = 100 + 30 * Math.min(maxCount, genres.length);
  return (
    <>
      <h3>Top genres by liked tracks</h3>
      <BarChart
        h={height}
        data={genres
          .sort((a, b) => b.liked_track_count - a.liked_track_count)
          .slice(0, maxCount)
          .map((p) => ({
            Genre: p.genre,
            Liked: p.liked_track_count,
            Unliked: p.track_count - p.liked_track_count,
          }))}
        orientation="vertical"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        dataKey="Genre"
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
