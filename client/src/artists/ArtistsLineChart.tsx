import { LineChart } from "@mantine/charts";
import { Artist, ArtistRank } from "../api";
import { Paper } from "@mantine/core";
import { useIsMobile } from "../useIsMobile";

export function ArtistsLineChart({
  ranks,
  artists,
}: {
  ranks: ArtistRank[];
  artists: Record<string, Artist>;
}) {
  const isMobile = useIsMobile();
  const dataPoints = new Map<number, Record<string, number>>();
  const artistURIs = new Set<string>();

  for (const rank of ranks) {
    artistURIs.add(rank.artist_uri);
    const ts = new Date(rank.as_of_date).getTime();

    const existing = dataPoints.get(ts);
    if (existing) {
      existing[rank.artist_uri] = rank.artist_rank;
    } else {
      dataPoints.set(ts, {
        date: ts,
        [rank.artist_uri]: rank.artist_rank,
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
      h="80vh"
      data={Array.from(dataPoints.values()).sort(
        (a, b) => a["date"] - b["date"]
      )}
      dataKey="date"
      series={Array.from(artistURIs).map((uri, i) => ({
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
          <ArtistsLegend payload={payload} artists={artists} />
        ),
      }}
      withTooltip={!isMobile}
      tooltipProps={{
        content: ({ label, payload }) => (
          <ArtistsTooltip
            label={label}
            payload={payload ?? []}
            artists={artists}
          />
        ),
      }}
    />
  );
}

interface ArtistsTooltipProps {
  label?: number;
  payload: TooltipItem[];
  artists: Record<string, Artist>;
}

interface TooltipItem {
  value?: number;
  name?: string;
  color?: string;
}

function ArtistsTooltip({ label, payload, artists }: ArtistsTooltipProps) {
  return (
    <Paper
      withBorder
      style={{ display: "flex", flexDirection: "column", padding: 20, gap: 5 }}
    >
      <h3 style={{ margin: 0, alignSelf: "center" }}>{formatDate(label)}</h3>
      {payload
        ?.sort((a, b) => (a.value ?? 0) - (b.value ?? 0))
        .map((item) => {
          const artist = item.name ? artists[item.name] : undefined;
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
                src={artist?.artist_image_url}
                style={{ height: "1.5em", width: "1.5em" }}
              />
              <span>{artist?.artist_name}</span>
            </div>
          );
        })}
    </Paper>
  );
}

interface ArtistsLegendProps {
  payload?: LegendItem[];
  artists: Record<string, Artist>;
}

interface LegendItem {
  color?: string;
  value: string;
}

function ArtistsLegend({ payload, artists }: ArtistsLegendProps) {
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
          const artist = artists[item.value];
          return { item, artist };
        })
        .sort((a, b) => a.artist.artist_rank - b.artist.artist_rank)
        .map(({ item, artist }) => {
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
                src={artist?.artist_image_url}
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
                {artist?.artist_name}
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
