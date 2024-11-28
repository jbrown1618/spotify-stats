import { BarChart } from "@mantine/charts";
import { ArtistTrackCount } from "../api";

export function ArtistsBarChart({ counts }: { counts: ArtistTrackCount[] }) {
  return (
    <BarChart
      h={800}
      data={Object.values(counts)
        .sort((a, b) => b.artist_liked_track_count - a.artist_liked_track_count)
        .slice(0, 20)
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
      withLegend
      legendProps={{ verticalAlign: "bottom" }}
      gridAxis="y"
    />
  );
}
