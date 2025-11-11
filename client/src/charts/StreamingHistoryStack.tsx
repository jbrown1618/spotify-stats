import { Button } from "@mantine/core";
import { IconMinus, IconPlus } from "@tabler/icons-react";
import { useRef } from "react";

import { colors } from "./colors";
import { StreamingHistoryAreaChart } from "./StreamingHistoryAreaChart";

const itemHeaderHeight = 32;
const xAxisHeight = 15;
const individualMaxHeight = 250;
const totalMinHeight = 600;
const individualMinHeight = 120;

export function StreamingHistoryStack<TItem>({
  data,
  getItem,
  renderItem,
  sortItems,
  onMore,
  onLess,
}: {
  data: Record<string, Record<number, Record<number, number>>>;
  renderItem: (item: TItem) => JSX.Element;
  getItem: (key: string) => TItem;
  sortItems: (a: TItem, b: TItem) => number;
  onMore?: () => void;
  onLess?: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const dataMax = Math.max(
    ...[...forEachDataPoint(data)].map((d) => d.streams)
  );
  const minYear = Math.min(...[...forEachDataPoint(data)].map((d) => d.year));
  const minMonth = Math.min(
    ...[...forEachDataPoint(data)]
      .filter((d) => d.year === minYear)
      .map((d) => d.month)
  );

  const maxYear = Math.max(...[...forEachDataPoint(data)].map((d) => d.year));
  const maxMonth = Math.max(
    ...[...forEachDataPoint(data)]
      .filter((d) => d.year === maxYear)
      .map((d) => d.month)
  );

  const itemCount = Object.keys(data).length;
  const totalMaxHeight = Math.max(
    totalMinHeight,
    itemCount * individualMinHeight
  );
  const itemHeight = Math.min(
    individualMaxHeight,
    (totalMaxHeight - xAxisHeight - itemHeaderHeight * itemCount) / itemCount
  );
  return (
    <div ref={ref} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {Object.keys(data)
        .filter(getItem)
        .sort((a, b) => sortItems(getItem(a), getItem(b)))
        .map((key, i) => (
          <div key={key}>
            <div style={{ marginLeft: 0 }}>{renderItem(getItem(key))}</div>
            <div style={{ marginLeft: -25 }}>
              <StreamingHistoryAreaChart
                streams_by_month={data[key]}
                height={
                  i === Object.keys(data).length - 1
                    ? itemHeight + 15
                    : itemHeight
                }
                color={colors[i % colors.length]}
                withXAxis={i === Object.keys(data).length - 1}
                dataMax={dataMax}
                minYear={minYear}
                minMonth={minMonth}
                maxYear={maxYear}
                maxMonth={maxMonth}
              />
            </div>
          </div>
        ))}
      <div
        style={{ display: "flex", gap: 8, marginTop: 8, alignSelf: "flex-end" }}
      >
        {onLess && (
          <Button
            size="compact-md"
            variant="light"
            onClick={() => {
              onLess();
              ref.current?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            <IconMinus />
          </Button>
        )}
        {onMore && (
          <Button onClick={onMore} size="compact-md" variant="light">
            <IconPlus />
          </Button>
        )}
      </div>
    </div>
  );
}

function* forEachDataPoint(
  data: Record<string, Record<number, Record<number, number>>>
): Generator<{ key: string; year: number; month: number; streams: number }> {
  for (const [key, byYear] of Object.entries(data)) {
    for (const [year, byMonth] of Object.entries(byYear)) {
      for (const [month, streams] of Object.entries(byMonth)) {
        yield { key, year: parseInt(year), month: parseInt(month), streams };
      }
    }
  }
}
