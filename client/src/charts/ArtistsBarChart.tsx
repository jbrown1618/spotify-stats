import { BarChart } from "@mantine/charts";

import { ChartSkeleton } from "../design/ChartSkeleton";
import { useArtists } from "../useApi";
import { useIsMobile } from "../useIsMobile";
import { allBarValuesAreOne } from "./utils";

export function ArtistsBarChart() {
  const isMobile = useIsMobile();
  const maxCount = isMobile ? 15 : 20;
  const { items: artists, total } = useArtists({ sort: "Most liked tracks", limit: maxCount });

  if (total < 3) return null;

  if (!artists) return <ChartSkeleton />;

  const data = artists
    .map((p) => ({
      Artist: p.artist_name,
      Liked: p.artist_liked_track_count,
      Unliked: p.artist_track_count - p.artist_liked_track_count,
    }));

  if (allBarValuesAreOne(data)) return null;

  const height = 100 + 30 * Math.min(maxCount, artists.length);
  return (
    <>
      <h3>Artists by liked tracks</h3>
      <BarChart
        h={height}
        data={data}
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
