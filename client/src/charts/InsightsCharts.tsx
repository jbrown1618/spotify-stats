import { BarChart, LineChart } from "@mantine/charts";
import { Text } from "@mantine/core";

import {
  ReleaseMonthCount,
  StreamDistributionBucket,
  TotalStreamsMonth,
  TrackDiscoveryMonth,
  TrackVarietyMonth,
} from "../api";
import { useIsMobile } from "../useIsMobile";
import { formatMonth } from "../utils";

type DistributionEntity = StreamDistributionBucket["entity_type"];

const streamBuckets = [
  "0",
  "1",
  "2",
  "3-5",
  "6-10",
  "11-20",
  "21-50",
  "51-100",
  "101-200",
  "201-500",
  "501-1k",
  "1k-2k",
  "2k-4k",
  "4k+",
];
const distributionCharts: {
  entity: DistributionEntity;
  label: string;
  color: string;
}[] = [
  { entity: "track", label: "Tracks", color: "green" },
  { entity: "artist", label: "Artists", color: "blue" },
  { entity: "album", label: "Albums", color: "grape" },
];
const monthLabels = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

function monthTimestamp(month: string): number {
  return new Date(`${month}-01T00:00:00`).getTime();
}

export function TotalStreamsByMonthChart({
  totalStreams,
}: {
  totalStreams: TotalStreamsMonth[];
}) {
  const isMobile = useIsMobile();
  if (totalStreams.length < 2) return null;

  const data = totalStreams.map((item) => ({
    Month: monthTimestamp(item.month),
    Streams: item.stream_count,
  }));

  return (
    <>
      <h3>Total streams by month</h3>
      <LineChart
        h={288}
        data={data}
        dataKey="Month"
        series={[{ name: "Streams", color: "green" }]}
        withDots={false}
        withTooltip={!isMobile}
        xAxisProps={{ tickFormatter: formatMonth }}
      />
    </>
  );
}

export function StreamDistributionsChart({
  distributions,
}: {
  distributions: StreamDistributionBucket[];
}) {
  if (distributions.length === 0) return null;

  return (
    <>
      {distributionCharts.map((chart) => (
        <StreamDistributionChart
          key={chart.entity}
          distributions={distributions}
          entity={chart.entity}
          label={chart.label}
          color={chart.color}
        />
      ))}
    </>
  );
}

function StreamDistributionChart({
  distributions,
  entity,
  label,
  color,
}: {
  distributions: StreamDistributionBucket[];
  entity: DistributionEntity;
  label: string;
  color: string;
}) {
  const isMobile = useIsMobile();
  const countsByBucket = new Map(
    distributions
      .filter((item) => item.entity_type === entity)
      .map((item) => [item.bucket, item.item_count])
  );
  const data = streamBuckets.map((bucket) => ({
    Streams: bucket,
    [label]: countsByBucket.get(bucket) ?? 0,
  }));

  return (
    <>
      <h3>Streams per {entity}</h3>
      <BarChart
        h={256}
        data={data}
        dataKey="Streams"
        series={[{ name: label, color }]}
        withTooltip={!isMobile}
        withBarValueLabel={isMobile}
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
        h={288}
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
        h={288}
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
      <Text c="dimmed">
        When listening is evenly distributed, effective tracks matches unique
        tracks. The bigger the gap, the more skewed that month was toward a few
        tracks.
      </Text>
      <LineChart
        h={288}
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
