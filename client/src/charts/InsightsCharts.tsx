import { BarChart, LineChart } from "@mantine/charts";
import { Text } from "@mantine/core";

import {
  ReleaseMonthCount,
  StreamDistributionBucket,
  TrackDiscoveryMonth,
  TrackVarietyMonth,
} from "../api";
import { useIsMobile } from "../useIsMobile";
import { formatMonth } from "../utils";

const streamBuckets = ["0", "1", "2", "3-5", "6-10", "11-20", "21-50", "51-100", "101+"];
const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function monthTimestamp(month: string): number {
  return new Date(`${month}-01T00:00:00`).getTime();
}

export function StreamDistributionsChart({
  distributions,
}: {
  distributions: StreamDistributionBucket[];
}) {
  const isMobile = useIsMobile();
  if (distributions.length === 0) return null;

  const countsByEntityAndBucket = new Map<string, number>();
  for (const item of distributions) {
    countsByEntityAndBucket.set(
      `${item.entity_type}:${item.bucket}`,
      item.item_count
    );
  }

  const data = streamBuckets.map((bucket) => ({
    Streams: bucket,
    Tracks: countsByEntityAndBucket.get(`track:${bucket}`) ?? 0,
    Artists: countsByEntityAndBucket.get(`artist:${bucket}`) ?? 0,
    Albums: countsByEntityAndBucket.get(`album:${bucket}`) ?? 0,
  }));

  return (
    <>
      <h3>Streams per track, artist, and album</h3>
      <BarChart
        h={360}
        data={data}
        dataKey="Streams"
        series={[
          { name: "Tracks", color: "green" },
          { name: "Artists", color: "blue" },
          { name: "Albums", color: "grape" },
        ]}
        withLegend
        withTooltip={!isMobile}
        withBarValueLabel={isMobile}
        legendProps={{ verticalAlign: "bottom" }}
        gridAxis="y"
      />
    </>
  );
}

export function ReleaseMonthsChart({
  releaseMonths,
}: {
  releaseMonths: ReleaseMonthCount[];
}) {
  const isMobile = useIsMobile();
  if (releaseMonths.length < 2) return null;

  const countsByMonth = new Map(
    releaseMonths.map((item) => [item.release_month, item])
  );
  const data = monthLabels.map((month, index) => {
    const item = countsByMonth.get(index + 1);
    const liked = item?.liked_track_count ?? 0;
    const total = item?.track_count ?? 0;
    return {
      Month: month,
      Liked: liked,
      Unliked: total - liked,
    };
  });

  return (
    <>
      <h3>Tracks by release month</h3>
      <BarChart
        h={360}
        data={data}
        dataKey="Month"
        series={[
          { name: "Liked", color: "green" },
          { name: "Unliked", color: "gray" },
        ]}
        type="stacked"
        withLegend
        withTooltip={!isMobile}
        withBarValueLabel={isMobile}
        legendProps={{ verticalAlign: "bottom" }}
        gridAxis="y"
      />
    </>
  );
}

export function TrackDiscoveryChart({
  discovery,
}: {
  discovery: TrackDiscoveryMonth[];
}) {
  const isMobile = useIsMobile();
  if (discovery.length < 2) return null;

  const data = discovery.map((item) => ({
    Month: monthTimestamp(item.month),
    "First streams": item.first_stream_count,
    "Replayed discoveries": item.retained_track_count,
  }));

  return (
    <>
      <h3>Track discovery over time</h3>
      <Text c="dimmed">
        Replayed discoveries are tracks first heard in that month that were
        streamed again after that first listen.
      </Text>
      <LineChart
        h={360}
        data={data}
        dataKey="Month"
        series={[
          { name: "First streams", color: "green" },
          { name: "Replayed discoveries", color: "blue" },
        ]}
        withDots={false}
        withLegend
        withTooltip={!isMobile}
        legendProps={{ verticalAlign: "bottom" }}
        xAxisProps={{ tickFormatter: formatMonth }}
      />
    </>
  );
}

export function TrackVarietyChart({
  variety,
}: {
  variety: TrackVarietyMonth[];
}) {
  const isMobile = useIsMobile();
  if (variety.length < 2) return null;

  const data = variety.map((item) => ({
    Month: monthTimestamp(item.month),
    "Effective tracks": Number(item.effective_track_count.toFixed(1)),
    "Unique tracks": item.unique_track_count,
  }));

  return (
    <>
      <h3>Listening variety over time</h3>
      <Text c="dimmed">
        Effective tracks estimates how many evenly played tracks would produce
        the same listening balance for each month.
      </Text>
      <LineChart
        h={360}
        data={data}
        dataKey="Month"
        series={[
          { name: "Effective tracks", color: "green" },
          { name: "Unique tracks", color: "gray" },
        ]}
        withDots={false}
        withLegend
        withTooltip={!isMobile}
        legendProps={{ verticalAlign: "bottom" }}
        xAxisProps={{ tickFormatter: formatMonth }}
      />
    </>
  );
}
