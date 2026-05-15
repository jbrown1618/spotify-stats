import { Pill } from "@mantine/core";

import { LabelsBarChart } from "../charts/LabelsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { usePaginatedLabels } from "../useApi";
import { useFilters, useSetFilters } from "../useFilters";
import styles from "./Sections.module.css";

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
  const { data, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    usePaginatedLabels();

  const items = data?.pages.flatMap((p) => p.items);
  const total = data?.pages[0]?.total ?? 0;

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(ltc) => ltc.label}
      renderPill={(ltc) => <RecordLabelPill label={ltc.label} />}
      hasNextPage={hasNextPage}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}

function RecordLabelPill({ label }: { label: string }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      className={styles.clickable}
      onClick={() => setFilters({ labels: [label] })}
    >
      {label}
    </Pill>
  );
}
