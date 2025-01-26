import { colors } from "./colors";
import { StreamingHistoryAreaChart } from "./StreamingHistoryAreaChart";

export function StreamingHistoryStack<TItem>({
  data,
  getItem,
  renderItem,
  sortItems,
}: {
  data: Record<string, Record<number, Record<number, number>>>;
  renderItem: (item: TItem) => JSX.Element;
  getItem: (key: string) => TItem;
  sortItems: (a: TItem, b: TItem) => number;
}) {
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
  const itemHeight = (550 - 32 * itemCount) / itemCount;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {Object.keys(data)
        .sort((a, b) => sortItems(getItem(a), getItem(b)))
        .map((key, i) => (
          <div>
            <div style={{ marginLeft: 30 }}>{renderItem(getItem(key))}</div>
            <StreamingHistoryAreaChart
              streams_by_month={data[key]}
              height={itemHeight}
              color={colors[i]}
              dataMax={dataMax}
              minYear={minYear}
              minMonth={minMonth}
              maxYear={maxYear}
              maxMonth={maxMonth}
            />
          </div>
        ))}
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
