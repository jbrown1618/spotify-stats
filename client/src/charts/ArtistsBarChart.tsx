import { BarChart } from "@mantine/charts";

import { ArtistTrackCount } from "../api";
import { useIsMobile } from "../useIsMobile";

export function ArtistsBarChart({ counts }: { counts: ArtistTrackCount[] }) {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(counts).length);
  return (
    <BarChart
      h={height}
      data={Object.values(counts)
        .sort((a, b) => b.artist_liked_track_count - a.artist_liked_track_count)
        .slice(0, maxCount)
        .map((p) => ({
          Artist: p.artist_name,
          Liked: p.artist_liked_track_count,
          Unliked: p.artist_track_count - p.artist_liked_track_count,
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
  );
}
