import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useReleaseYears } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function YearsBarChart() {
  const { data: years } = useReleaseYears();
  const isMobile = useIsMobile();

  if (!years) return <ChartSkeleton />;
  if (years && years.length < 3) return null;

  const distinctYears = new Set(years.map((c) => c.release_year));
  const minYear = Math.min(...distinctYears);
  const maxYear = Math.max(...distinctYears);

  for (let y = minYear + 1; y < maxYear; y++) {
    if (!distinctYears.has(y)) {
      years.push({
        release_year: y,
        liked_track_count: 0,
        track_count: 0,
        total_liked_track_count: 0,
        total_track_count: 0,
      });
    }
  }

  return (
    <>
      <h3>Liked tracks by release year</h3>
      <BarChart
        h={500}
        data={years
          .sort((a, b) => (a.release_year > b.release_year ? 1 : -1))
          .map((p) => ({
            Year: p.release_year,
            Liked: p.liked_track_count,
            Unliked: p.track_count - p.liked_track_count,
          }))}
        orientation="horizontal"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        dataKey="Year"
        type="stacked"
        withLegend
        withTooltip={!isMobile}
        withBarValueLabel={isMobile && distinctYears.size < 8}
        legendProps={{ verticalAlign: "bottom" }}
        gridAxis="none"
      />
    </>
  );
}
