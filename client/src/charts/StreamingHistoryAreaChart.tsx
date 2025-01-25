import { AreaChart } from "@mantine/charts";

import { useIsMobile } from "../useIsMobile";

export function StreamingHistoryLineChart({
  streams_by_month,
  height,
}: {
  streams_by_month: Record<number, Record<number, number>>;
  height?: number;
}) {
  const isMobile = useIsMobile();
  const data = prepareData(streams_by_month);
  return (
    <AreaChart
      h={height ?? 500}
      data={data}
      dataKey="Month"
      series={[{ name: "Streams", color: "green" }]}
      connectNulls={false}
      withDots={false}
      withTooltip={!isMobile}
      withGradient={false}
    />
  );
}

function prepareData(
  input: Record<number, Record<number, number>>
): { Month: string; Streams: number }[] {
  const minYear = Math.min(...Object.keys(input).map((y) => parseInt(y)));
  const maxYear = Math.max(...Object.keys(input).map((y) => parseInt(y)));
  const minMonthInMinYear = Math.min(
    ...Object.keys(input[minYear]).map((m) => parseInt(m))
  );
  const maxMonthInMaxYear = Math.max(
    ...Object.keys(input[maxYear]).map((m) => parseInt(m))
  );

  let y = minYear;
  let m = minMonthInMinYear;
  while (y < maxYear || m < maxMonthInMaxYear) {
    if (!input[y]) {
      input[y] = {};
    }
    if (!input[y][m]) {
      input[y][m] = 0;
    }
    ++m;
    if (m > 12) {
      m = 1;
      ++y;
    }
  }

  const data: { Month: string; Streams: number }[] = [];
  for (const [year, by_month] of Object.entries(input)) {
    for (const [month, streams] of Object.entries(by_month)) {
      data.push({
        Month: `${year}-${month}`,
        Streams: streams,
      });
    }
  }
  return data;
}
