import { BarChart } from "@mantine/charts";
import { PlaylistTrackCount } from "../api";

export function PlaylistsBarChart({
  counts,
}: {
  counts: PlaylistTrackCount[];
}) {
  return (
    <BarChart
      h={800}
      data={Object.values(counts)
        .sort(
          (a, b) => b.playlist_liked_track_count - a.playlist_liked_track_count
        )
        .slice(0, 20)
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
      withLegend
      legendProps={{ verticalAlign: "bottom" }}
      gridAxis="y"
    />
  );
}
