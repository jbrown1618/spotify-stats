import { colors } from "./colors";
import { StreamingHistoryAreaChart } from "./StreamingHistoryAreaChart";
export function StreamingHistoryStack({
  data,
  renderKey,
}: {
  data: Record<string, Record<number, Record<number, number>>>;
  renderKey: (key: string) => JSX.Element;
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

  const itemCount = Object.keys(data).length;
  const itemHeight = (550 - 32 * itemCount) / itemCount;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {Object.keys(data).map((key, i) => (
        <div>
          <div style={{ marginLeft: 30 }}>{renderKey(key)}</div>
          <StreamingHistoryAreaChart
            streams_by_month={data[key]}
            height={itemHeight}
            color={colors[i]}
            dataMax={dataMax}
            minYear={minYear}
            minMonth={minMonth}
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
