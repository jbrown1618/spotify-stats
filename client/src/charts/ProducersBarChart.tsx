import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useProducers } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function ProducersBarChart() {
  const { data: producers } = useProducers();
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  if (!producers) return <ChartSkeleton />;

  const height = 100 + 30 * Math.min(maxCount, Object.values(producers).length);
  return (
    <>
      <h3>Top producers by liked tracks</h3>
      <BarChart
        h={height}
        data={Object.values(producers)
          .sort((a, b) => b.liked_track_count - a.liked_track_count)
          .slice(0, maxCount)
          .map((p) => ({
            Producer: p.producer_name,
            Liked: p.liked_track_count,
            Unliked: p.track_count - p.liked_track_count,
          }))}
        orientation="vertical"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        dataKey="Producer"
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
