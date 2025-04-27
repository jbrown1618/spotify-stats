import { LineChart } from "@mantine/charts";
import { Paper } from "@mantine/core";

import { useIsMobile } from "../useIsMobile";
import { formatDate } from "../utils";
import { colors } from "./colors";

interface RankLineChartProps<TStreams> {
  ranks: TStreams[];
  height?: number;
  getKey: (r: TStreams) => string;
  getStreams: (r: TStreams) => number;
  getDate: (r: TStreams) => string;
  getItem: (r: TStreams) => string;
  getCurrentRank: (k: string) => number;
  getLabel: (k: string) => string;
  getImageURL: (k: string) => string;
}

export function StreamsLineChart<TStreams>({
  ranks,
  height,
  getKey,
  getStreams,
  getDate,
  getLabel,
  getCurrentRank,
  getImageURL,
}: RankLineChartProps<TStreams>) {
  const isMobile = useIsMobile();

  const dataPoints = new Map<number, Record<string, number>>();
  const uris = new Set<string>();

  for (const rank of ranks) {
    uris.add(getKey(rank));

    const ts = new Date(getDate(rank)).getTime();

    const existing = dataPoints.get(ts);
    if (existing) {
      existing[getKey(rank)] = getStreams(rank);
    } else {
      dataPoints.set(ts, {
        date: ts,
        [getKey(rank)]: getStreams(rank),
      });
    }
  }

  // Add a 0 to the data point immediately before the first stream for this URI
  const minTs = Math.min(...dataPoints.keys());
  for (const uri of uris) {
    const minTsForUri = Math.min(
      ...[...dataPoints.entries()]
        .filter(([_, values]) => !!values[uri])
        .map(([ts]) => ts)
    );
    if (minTsForUri === minTs) continue;

    const previousTs = Math.max(
      ...[...dataPoints.keys()].filter((ts) => ts < minTsForUri)
    );
    const streamsByUri = dataPoints.get(previousTs)!;
    streamsByUri[uri] = 0;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <LineChart
        h={height ?? 550}
        data={Array.from(dataPoints.values()).sort(
          (a, b) => a["date"] - b["date"]
        )}
        dataKey="date"
        series={Array.from(uris).map((uri, i) => ({
          name: uri,
          color: colors[i],
        }))}
        connectNulls={false}
        withDots={false}
        xAxisProps={{
          tickFormatter: formatDate,
        }}
        withLegend={isMobile}
        legendProps={{
          verticalAlign: "bottom",
          content: ({ payload }) => (
            <RankLineChartLegend
              payload={payload}
              getLabel={getLabel}
              getImageURL={getImageURL}
              getStreamCount={getCurrentRank}
            />
          ),
        }}
        withTooltip={!isMobile}
        tooltipProps={{
          content: ({ label, payload }) => (
            <RankLineChartTooltip
              label={label}
              payload={payload ?? []}
              getLabel={getLabel}
              getImageURL={getImageURL}
            />
          ),
        }}
      />
    </div>
  );
}

interface RankLineChartTooltipProps {
  label?: number;
  payload: TooltipItem[];
  getImageURL: (k: string) => string;
  getLabel: (k: string) => string;
}

interface TooltipItem {
  value?: number;
  name?: string;
  color?: string;
}

function RankLineChartTooltip({
  label,
  payload,
  getImageURL,
  getLabel,
}: RankLineChartTooltipProps) {
  return (
    <Paper
      withBorder
      style={{ display: "flex", flexDirection: "column", padding: 20, gap: 5 }}
    >
      <h3 style={{ margin: 0, alignSelf: "center" }}>{formatDate(label)}</h3>
      {payload
        ?.sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
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
              <span style={{ width: 30, textAlign: "right" }}>
                {item.value}
              </span>
              <img
                src={item.name && getImageURL(item.name)}
                style={{ height: "1.5em", width: "1.5em" }}
              />
              <span>{item.name && getLabel(item.name)}</span>
            </div>
          );
        })}
    </Paper>
  );
}

interface StreamsLineChartLegendProps {
  payload?: LegendItem[];
  getImageURL: (k: string) => string;
  getLabel: (k: string) => string;
  getStreamCount: (k: string) => number;
}

interface LegendItem {
  color?: string;
  value: string;
}

function RankLineChartLegend({
  payload,
  getImageURL,
  getLabel,
  getStreamCount,
}: StreamsLineChartLegendProps) {
  if (!payload) return null;
  return (
    <div
      style={{
        margin: 16,
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        gap: 8,
      }}
    >
      {payload
        .sort((a, b) => getStreamCount(a.value) - getStreamCount(b.value))
        .map((item) => {
          return (
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                gap: 8,
              }}
            >
              <div
                style={{
                  backgroundColor: item.color,
                  height: "1em",
                  width: "1em",
                  borderRadius: "0.5em",
                }}
              />
              <img
                src={getImageURL(item.value)}
                style={{ height: "1.5em", width: "1.5em" }}
              />
              <span
                style={{
                  width: "20vw",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                  textOverflow: "ellipsis",
                }}
              >
                {getLabel(item.value)}
              </span>
            </div>
          );
        })}
    </div>
  );
}
