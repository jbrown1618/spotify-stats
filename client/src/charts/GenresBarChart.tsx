import { BarChart } from "@mantine/charts";

import { GenreTrackCount } from "../api";
import { useIsMobile } from "../useIsMobile";

export function GenresBarChart({ counts }: { counts: GenreTrackCount[] }) {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(counts).length);
  return (
    <BarChart
      h={height}
      data={Object.values(counts)
        .sort((a, b) => b.genre_liked_track_count - a.genre_liked_track_count)
        .slice(0, maxCount)
        .map((p) => ({
          Genre: p.genre,
          Liked: p.genre_liked_track_count,
          Unliked: p.genre_track_count - p.genre_liked_track_count,
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
  );
}
