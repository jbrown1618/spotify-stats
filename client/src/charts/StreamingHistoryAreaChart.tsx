import { AreaChart } from "@mantine/charts";

import { useIsMobile } from "../useIsMobile";

export function StreamingHistoryAreaChart({
  streams_by_month,
  height,
  color,
  dataMax,
  minYear,
  minMonth,
}: {
  streams_by_month: Record<number, Record<number, number>>;
  height?: number;
  color?: string;
  dataMax?: number;
  minYear?: number;
  minMonth?: number;
}) {
  const isMobile = useIsMobile();
  minYear ??= Math.min(
    ...Object.keys(streams_by_month).map((y) => parseInt(y))
  );
  minMonth ??= Math.min(
    ...Object.keys(streams_by_month[minYear]).map((m) => parseInt(m))
  );
  const maxYear = Math.max(
    ...Object.keys(streams_by_month).map((y) => parseInt(y))
  );
  const maxMonth = Math.max(
    ...Object.keys(streams_by_month[maxYear]).map((m) => parseInt(m))
  );

  let y = minYear;
  let m = minMonth;
  while (y < maxYear || m < maxMonth) {
    if (!streams_by_month[y]) {
      streams_by_month[y] = {};
    }
    if (!streams_by_month[y][m]) {
      streams_by_month[y][m] = 0;
    }
    ++m;
    if (m > 12) {
      m = 1;
      ++y;
    }
  }

  const data: { Month: string; Streams: number }[] = [];
  for (const [year, by_month] of Object.entries(streams_by_month)) {
    for (const [month, streams] of Object.entries(by_month)) {
      data.push({
        Month: `${year}-${month}`,
        Streams: streams,
      });
    }
  }
  return (
    <AreaChart
      h={height ?? 500}
      data={data}
      dataKey="Month"
      series={[{ name: "Streams", color: color ?? "green" }]}
      connectNulls={false}
      withDots={false}
      withTooltip={!isMobile}
      withGradient={false}
      yAxisProps={
        dataMax
          ? {
              domain: [() => 0, () => dataMax],
            }
          : undefined
      }
    />
  );
}
