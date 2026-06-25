import { Text } from "@mantine/core";

import {
  ReleaseMonthsChart,
  StreamDistributionsChart,
  TrackDiscoveryChart,
  TrackVarietyChart,
} from "../charts/InsightsCharts";
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

      <TrackDiscoveryChart discovery={insights.discovery} />
      <TrackVarietyChart variety={insights.variety} />
      <StreamDistributionsChart distributions={insights.distributions} />
      <ReleaseMonthsChart releaseMonths={insights.release_months} />

      {insights.discovery.length === 0 &&
        insights.variety.length === 0 &&
        insights.distributions.length === 0 &&
        insights.release_months.length === 0 && (
          <Text fs="italic">No insight data</Text>
        )}
    </div>
  );
}
