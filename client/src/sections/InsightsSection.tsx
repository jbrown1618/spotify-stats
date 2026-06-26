import { Text } from "@mantine/core";

import {
  ReleaseMonthsChart,
  StreamDistributionsChart,
  TotalStreamsByMonthChart,
  TrackDiscoveryChart,
  TrackVarietyChart,
} from "../charts/InsightsCharts";
import {
  HourByWeekdayHeatmap,
  MonthByYearHeatmap,
  WeekdayByMonthHeatmap,
} from "../charts/ListeningHeatmaps";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { useInsights } from "../useApi";

export function InsightsSection() {
  const { data: insights, isLoading } = useInsights();

  if (isLoading || !insights) {
    return <ChartSkeleton />;
  }

  return (
    <div>
      <h2>Insights</h2>

      <TotalStreamsByMonthChart totalStreams={insights.total_streams} />
      <WeekdayByMonthHeatmap values={insights.weekday_by_month} />
      <MonthByYearHeatmap values={insights.month_by_year} />
      <HourByWeekdayHeatmap values={insights.hour_by_weekday} />
      <TrackDiscoveryChart discovery={insights.discovery} />
      <TrackVarietyChart variety={insights.variety} />
      <StreamDistributionsChart distributions={insights.distributions} />
      <ReleaseMonthsChart releaseMonths={insights.release_months} />

      {insights.discovery.length === 0 &&
        insights.variety.length === 0 &&
        insights.total_streams.length === 0 &&
        insights.weekday_by_month.length === 0 &&
        insights.month_by_year.length === 0 &&
        insights.hour_by_weekday.length === 0 &&
        insights.distributions.length === 0 &&
        insights.release_months.length === 0 && (
          <Text fs="italic">No insight data</Text>
        )}
    </div>
  );
}
