import { BarChart } from "@mantine/charts";

import { PlaylistTrackCount } from "../api";
import { useIsMobile } from "../useIsMobile";

export function PlaylistsBarChart({
  counts,
}: {
  counts: PlaylistTrackCount[];
}) {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;
  const height = 100 + 30 * Math.min(maxCount, Object.keys(counts).length);
  return (
    <BarChart
      h={height}
      data={Object.values(counts)
        .sort(
          (a, b) => b.playlist_liked_track_count - a.playlist_liked_track_count
        )
        .slice(0, maxCount)
        .map((p) => ({
          Playlist: p.playlist_name,
          Liked: p.playlist_liked_track_count,
          Unliked: p.playlist_track_count - p.playlist_liked_track_count,
        }))}
      orientation="vertical"
      series={[
        { name: "Liked", color: "green" },
        { name: "Unliked", color: "gray" },
      ]}
      dataKey="Playlist"
      type="stacked"
      withTooltip={!isMobile}
      withBarValueLabel={isMobile}
      withLegend
      legendProps={{ verticalAlign: "bottom" }}
      gridAxis="y"
    />
  );
}