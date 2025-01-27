import { AreaChart } from "@mantine/charts";
import { Paper } from "@mantine/core";

import { useIsMobile } from "../useIsMobile";
import { formatMonth } from "../utils";

export function StreamingHistoryAreaChart({
  streams_by_month,
  height,
  color,
  withXAxis,
  dataMax,
  minYear,
  minMonth,
  maxYear,
  maxMonth,
}: {
  streams_by_month: Record<number, Record<number, number>>;
  height?: number;
  color?: string;
  withXAxis?: boolean;
  dataMax?: number;
  minYear?: number;
  minMonth?: number;
  maxYear?: number;
  maxMonth?: number;
}) {
  const isMobile = useIsMobile();
  minYear ??= Math.min(
    ...Object.keys(streams_by_month).map((y) => parseInt(y))
  );
  minMonth ??= Math.min(
    ...Object.keys(streams_by_month[minYear]).map((m) => parseInt(m))
  );

  maxYear ??= Math.max(
    ...Object.keys(streams_by_month).map((y) => parseInt(y))
  );
  maxMonth ??= Math.max(
    ...Object.keys(streams_by_month[maxYear]).map((m) => parseInt(m))
  );

  let y = minYear;
  let m = minMonth;
  while (y < maxYear || (y === maxYear && m <= maxMonth)) {
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

  const data: { Month: number; Streams: number }[] = [];
  for (const [year, by_month] of Object.entries(streams_by_month)) {
    for (const [month, streams] of Object.entries(by_month)) {
      data.push({
        Month: new Date(parseInt(year), parseInt(month) - 1).getTime(),
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
      withXAxis={withXAxis ?? true}
      xAxisProps={{
        tickFormatter: formatMonth,
      }}
      tooltipProps={{
        content: ({ label, payload }) => (
          <AreaChartTooltip label={label} payload={payload ?? []} />
        ),
      }}
    />
  );
}

interface AreaChartTooltipProps {
  label?: number;
  payload: TooltipItem[];
}

interface TooltipItem {
  value?: number;
  name?: string;
  color?: string;
}

function AreaChartTooltip({ label, payload }: AreaChartTooltipProps) {
  return (
    <Paper
      withBorder
      style={{ display: "flex", flexDirection: "column", padding: 20, gap: 5 }}
    >
      <h3 style={{ margin: 0, alignSelf: "center" }}>{formatMonth(label)}</h3>
      {payload
        ?.sort((a, b) => (a.value ?? 0) - (b.value ?? 0))
        .map((item) => {
          return (
            <div style={{ display: "flex", flexDirection: "row", gap: 10 }}>
              <div
                style={{
                  backgroundColor: item.color,
                  height: "1em",
                  width: "1em",
                  borderRadius: "0.5em",
                }}
              />
              <span>Streams</span>
              <span style={{ width: 30, textAlign: "right" }}>
                {item.value}
              </span>
            </div>
          );
        })}
    </Paper>
  );
}
