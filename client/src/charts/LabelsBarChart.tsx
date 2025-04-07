import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useLabels } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function LabelsBarChart() {
  const { data: labels } = useLabels();
  const isMobile = useIsMobile();
  if (!labels) return <ChartSkeleton />;

  const maxCount = isMobile ? 15 : 20;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(labels).length);
  return (
    <>
      <h3>Top record labels by liked tracks</h3>
      <BarChart
        h={height}
        data={labels
          .sort((a, b) => b.liked_track_count - a.liked_track_count)
          .slice(0, maxCount)
          .map((p) => ({
            Label: p.label,
            Liked: p.liked_track_count,
            Unliked: p.track_count - p.liked_track_count,
          }))}
        orientation="vertical"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        dataKey="Label"
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
