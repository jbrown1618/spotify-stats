import { BarChart } from "@mantine/charts";
import { YearCounts } from "./api";

export function YearsBarChart({ counts }: { counts: YearCounts[] }) {
  const data = [...counts];

  const distinctYears = counts.map((c) => parseInt(c.year));
  const minYear = Math.min(...distinctYears);
  const maxYear = Math.max(...distinctYears);

  for (let y = minYear + 1; y < maxYear; y++) {
    if (!distinctYears.includes(y)) {
      data.push({
        year: String(y),
        liked: 0,
        total: 0,
      });
    }
  }

  return (
    <BarChart
      h={500}
      data={data
        .sort((a, b) => (a.year > b.year ? 1 : -1))
        .map((p) => ({
          Year: p.year,
          Liked: p.liked,
          Unliked: p.total - p.liked,
        }))}
      orientation="horizontal"
      series={[
        { name: "Liked", color: "green" },
        { name: "Unliked", color: "gray" },
      ]}
      dataKey="Year"
      type="stacked"
      withLegend
      legendProps={{ verticalAlign: "bottom" }}
      gridAxis="none"
    />
  );
}
