import { LineChart } from "@mantine/charts";
import { Paper, Slider, Text } from "@mantine/core";
import { useEffect, useState } from "react";

import { useIsMobile } from "../useIsMobile";
import { formatDate } from "../utils";
import { colors } from "./colors";

interface RankLineChartProps<TRank> {
  ranks: TRank[];
  height?: number;
  getKey: (r: TRank) => string;
  getRank: (r: TRank) => number;
  getDate: (r: TRank) => string;
  getItem: (r: TRank) => string;
  getCurrentRank: (k: string) => number;
  getLabel: (k: string) => string;
  getImageURL: (k: string) => string;
}

export function RankLineChart<TRank>({
  ranks,
  height,
  getKey,
  getRank,
  getDate,
  getItem,
  getLabel,
  getCurrentRank,
  getImageURL,
}: RankLineChartProps<TRank>) {
  const isMobile = useIsMobile();

  const dataPoints = new Map<number, Record<string, number>>();
  const artistURIs = new Set<string>();

  const range = getAxisRange(ranks, getRank, getItem, getDate);
  const [max, setMax] = useState(range.initialMax);

  useEffect(() => setMax(range.initialMax), [range.initialMax]);

  for (const rank of ranks) {
    artistURIs.add(getKey(rank));

    const ts = new Date(getDate(rank)).getTime();

    if (getRank(rank) > max) continue;

    const existing = dataPoints.get(ts);
    if (existing) {
      existing[getKey(rank)] = getRank(rank);
    } else {
      dataPoints.set(ts, {
        date: ts,
        [getKey(rank)]: getRank(rank),
      });
    }
  }

  height ??= 550;
  if (range.showSlider) {
    height -= 50;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <LineChart
        h={height ?? 500}
        data={Array.from(dataPoints.values()).sort(
          (a, b) => a["date"] - b["date"]
        )}
        dataKey="date"
        series={Array.from(artistURIs).map((uri, i) => ({
          name: uri,
          color: colors[i],
        }))}
        connectNulls={false}
        withDots={false}
        yAxisProps={{
          reversed: true,
          domain: [() => range.min, () => max],
        }}
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
              getCurrentRank={getCurrentRank}
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
      {range.showSlider && (
        <div style={{ margin: 8 }}>
          <Text>Scale</Text>
          <div style={{ flexGrow: 1 }}>
            <Slider
              value={max}
              onChange={setMax}
              min={range.maxSliderMin}
              max={range.max}
              label={(v) => `${Math.ceil(100 * (v / range.max))}%`}
            />
          </div>
        </div>
      )}
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

interface RankLineChartLegendProps {
  payload?: LegendItem[];
  getImageURL: (k: string) => string;
  getLabel: (k: string) => string;
  getCurrentRank: (k: string) => number;
}

interface LegendItem {
  color?: string;
  value: string;
}

function RankLineChartLegend({
  payload,
  getImageURL,
  getLabel,
  getCurrentRank,
}: RankLineChartLegendProps) {
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
        .sort((a, b) => getCurrentRank(a.value) - getCurrentRank(b.value))
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

interface AxisRange {
  min: number;
  max: number;
  initialMax: number;
  maxSliderMin: number;
  showSlider: boolean;
}

function getAxisRange<TRank>(
  ranks: TRank[],
  getRank: (r: TRank) => number,
  getItem: (r: TRank) => string,
  getDate: (r: TRank) => string
): AxisRange {
  const allRanks = ranks.map(getRank);
  const distinctItems = new Set(ranks.map(getItem)).size;
  const min = Math.min(...allRanks);
  const dataMax = Math.max(...allRanks);

  // The smallest max that should be settable
  const maxSliderMin = min + 9;
  const max = Math.max(dataMax, maxSliderMin);

  const maxDate = Math.max(...ranks.map((r) => new Date(getDate(r)).getTime()));

  const currentRanks = ranks
    .filter((r) => new Date(getDate(r)).getTime() === maxDate)
    .map(getRank);

  const minCurrentRank = Math.min(...currentRanks);
  const maxCurrentRank = Math.max(...currentRanks);

  const idealInitialMax = (maxCurrentRank - minCurrentRank) * 3 + min + 1;
  const showSlider = max - maxSliderMin > 20;

  const initialMax =
    showSlider && distinctItems > 1 ? Math.min(idealInitialMax, max) : max;

  return {
    min,
    max,
    initialMax,
    maxSliderMin,
    showSlider,
  };
}
