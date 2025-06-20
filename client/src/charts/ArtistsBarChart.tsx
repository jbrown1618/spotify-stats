import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostLikedArtists } from "../sorting";
import { useArtists } from "../useApi";
import { useIsMobile } from "../useIsMobile";

export function ArtistsBarChart() {
  const { data: artists } = useArtists();
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;

  if (artists && Object.keys(artists).length < 3) return null;

  if (!artists) return <ChartSkeleton />;

  const height = 100 + 30 * Math.min(maxCount, Object.keys(artists).length);
  return (
    <>
      <h3>Artists by liked tracks</h3>
      <BarChart
        h={height}
        data={Object.values(artists)
          .sort(mostLikedArtists)
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
    </>
  );
}
