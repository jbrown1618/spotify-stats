import { BarChart } from "@mantine/charts";

import { LabelTrackCount } from "../api";
import { useIsMobile } from "../useIsMobile";

export function LabelsBarChart({ counts }: { counts: LabelTrackCount[] }) {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(counts).length);
  return (
    <BarChart
      h={height}
      data={Object.values(counts)
        .sort((a, b) => b.label_liked_track_count - a.label_liked_track_count)
        .slice(0, maxCount)
        .map((p) => ({
          Label: p.label,
          Liked: p.label_liked_track_count,
          Unliked: p.label_track_count - p.label_liked_track_count,
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
  );
}
