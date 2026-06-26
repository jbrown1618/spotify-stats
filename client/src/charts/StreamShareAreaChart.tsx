import { AreaChart } from "@mantine/charts";
import { Text } from "@mantine/core";

import { StreamShareMonth } from "../api";
import { useIsMobile } from "../useIsMobile";
import { formatMonth } from "../utils";
import { colors } from "./colors";

function monthTimestamp(month: string): number {
  return new Date(`${month}-01T00:00:00`).getTime();
}

function chartKey(row: StreamShareMonth): string {
  return `${row.sort_order}:${row.category_key}`;
}

function formatShare(value: number): string {
  return `${value.toFixed(1).replace(/\.0$/, "")}%`;
}

export function StreamShareAreaChart({
  rows,
  title,
  description,
}: {
  rows: StreamShareMonth[];
  title: string;
  description: string;
}) {
  const isMobile = useIsMobile();
  if (rows.length === 0) return null;

  const categories = [
    ...new Map(
      rows
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((row) => [row.category_key, row])
    ).values(),
  ];
  const categoryLabels = new Map(
    categories.map((row) => [chartKey(row), row.category_name])
  );
  const categoryKeys = categories.map(chartKey);
  const rowsByMonth = new Map<number, Record<string, number>>();

  for (const row of rows) {
    const month = monthTimestamp(row.month);
    const existing = rowsByMonth.get(month) ?? { Month: month };
    existing[chartKey(row)] = Number((row.stream_share * 100).toFixed(2));
    rowsByMonth.set(month, existing);
  }

  const data = [...rowsByMonth.values()]
    .map((row) => {
      for (const category of categoryKeys) {
        row[category] ??= 0;
      }
      return row;
    })
    .sort((a, b) => a.Month - b.Month);

  return (
    <>
      <h3>{title}</h3>
      <Text c="dimmed">{description}</Text>
      <AreaChart
        h={360}
        data={data}
        dataKey="Month"
        series={categoryKeys.map((category, index) => ({
          name: category,
          label: categoryLabels.get(category),
          color:
            categoryLabels.get(category) === "Other"
              ? "gray"
              : colors[index % colors.length],
        }))}
        type="percent"
        withDots={false}
        withLegend
        withTooltip={!isMobile}
        legendProps={{ verticalAlign: "bottom" }}
        xAxisProps={{ tickFormatter: formatMonth }}
        yAxisProps={{ domain: [0, 1] }}
        valueFormatter={formatShare}
      />
    </>
  );
}
