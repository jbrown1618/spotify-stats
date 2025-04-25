import { Pill } from "@mantine/core";

import { LabelsBarChart } from "../charts/LabelsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useLabels } from "../useApi";
import { useFilters, useSetFilters } from "../useFilters";

export function LabelsSection() {
  const filters = useFilters();
  if (filters.labels?.length === 1) return null;
  return (
    <div>
      <h2>Record Labels</h2>
      <LabelsBarChart />
      <LabelsDisplayGrid />
    </div>
  );
}

function LabelsDisplayGrid() {
  const { data: labels, isLoading } = useLabels();
  return (
    <DisplayGrid
      loading={isLoading}
      items={
        labels
          ? labels.sort(
              (a, b) => (b.liked_track_count ?? 0) - (a.liked_track_count ?? 0)
            )
          : undefined
      }
      getKey={(ltc) => ltc.label}
      renderPill={(ltc) => <RecordLabelPill label={ltc.label} />}
    />
  );
}

function RecordLabelPill({ label }: { label: string }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      style={{ cursor: "pointer" }}
      onClick={() => setFilters({ labels: [label] })}
    >
      {label}
    </Pill>
  );
}
