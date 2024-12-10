import { LineChart } from "@mantine/charts";
import { Track, TrackRank } from "../api";
import { Paper } from "@mantine/core";
import { useIsMobile } from "../useIsMobile";

export function TracksLineChart({
  ranks,
  tracks,
}: {
  ranks: TrackRank[];
  tracks: Record<string, Track>;
}) {
  const isMobile = useIsMobile();
  const dataPoints = new Map<number, Record<string, number>>();
  const trackURIs = new Set<string>();

  for (const rank of ranks) {
    trackURIs.add(rank.track_uri);
    const ts = new Date(rank.as_of_date).getTime();

    const existing = dataPoints.get(ts);
    if (existing) {
      existing[rank.track_uri] = rank.track_rank;
    } else {
      dataPoints.set(ts, {
        date: ts,
        [rank.track_uri]: rank.track_rank,
      });
    }
  }

  const colors = [
    "#ea5545",
    "#f46a9b",
    "#ef9b20",
    "#edbf33",
    "#ede15b",
    "#bdcf32",
    "#87bc45",
    "#27aeef",
    "#b33dc6",
  ];

  return (
    <LineChart
      h={500}
      data={Array.from(dataPoints.values()).sort(
        (a, b) => a["date"] - b["date"]
      )}
      dataKey="date"
      series={Array.from(trackURIs).map((uri, i) => ({
        name: uri,
        color: colors[i],
      }))}
      withDots={false}
      yAxisProps={{ reversed: true }}
      xAxisProps={{
        tickFormatter: formatDate,
      }}
      withLegend={isMobile}
      legendProps={{
        verticalAlign: "bottom",
        content: ({ payload }) => (
          <TracksLegend payload={payload} tracks={tracks} />
        ),
      }}
      withTooltip={!isMobile}
      tooltipProps={{
        content: ({ label, payload }) => (
          <TracksTooltip
            label={label}
            payload={payload ?? []}
            tracks={tracks}
          />
        ),
      }}
    />
  );
}

interface TracksTooltipProps {
  label?: number;
  payload: TooltipItem[];
  tracks: Record<string, Track>;
}

interface TooltipItem {
  value?: number;
  name?: string;
  color?: string;
}

function TracksTooltip({ label, payload, tracks }: TracksTooltipProps) {
  return (
    <Paper
      withBorder
      style={{ display: "flex", flexDirection: "column", padding: 20, gap: 5 }}
    >
      <h3 style={{ margin: 0, alignSelf: "center" }}>{formatDate(label)}</h3>
      {payload
        ?.sort((a, b) => (a.value ?? 0) - (b.value ?? 0))
        .map((item) => {
          const track = item.name ? tracks[item.name] : undefined;
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
                src={track?.album_image_url}
                style={{ height: "1.5em", width: "1.5em" }}
              />
              <span>{track?.track_name}</span>
            </div>
          );
        })}
    </Paper>
  );
}

interface TracksLegendProps {
  payload?: LegendItem[];
  tracks: Record<string, Track>;
}

interface LegendItem {
  color?: string;
  value: string;
}

function TracksLegend({ payload, tracks }: TracksLegendProps) {
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
        .map((item) => {
          const track = tracks[item.value];
          return { item, track };
        })
        .sort((a, b) => a.track.track_rank - b.track.track_rank)
        .map(({ item, track }) => {
          return (
            <div
              style={{
                width: 140,
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
                src={track?.album_image_url}
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
                {track?.track_name}
              </span>
            </div>
          );
        })}
    </div>
  );
}

function formatDate(ts: number | undefined) {
  if (!ts) return "Unknown Date";
  const date = new Date(ts);
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDay()}`;
}
