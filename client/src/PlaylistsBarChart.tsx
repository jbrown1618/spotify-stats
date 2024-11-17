import { BarChart } from "@mantine/charts";
import { PlaylistTrackCount } from "./api";

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
          (a, b) => b.playlist_track_liked_count - a.playlist_track_liked_count
        )
        .slice(0, 20)
        .map((p) => ({
          Playlist: p.playlist_name,
          Liked: p.playlist_track_liked_count,
          Unliked: p.playlist_track_count - p.playlist_track_liked_count,
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
