import { Pill } from "@mantine/core";

import { LabelsBarChart } from "../charts/LabelsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PAGE_SIZE, useLabels } from "../useApi";
import { useSetFilters } from "../useFilters";
import { SectionHeading } from "./SectionHeading";
import styles from "./Sections.module.css";

export function LabelsSection() {
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useLabels({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <div>
      <SectionHeading title="Record Labels" total={total} />
      <LabelsBarChart />
      <DisplayGrid
        loading={isLoading}
        items={items}
        total={total}
        getKey={(ltc) => ltc.label}
        renderPill={(ltc) => <RecordLabelPill label={ltc.label} />}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={() => fetchNextPage()}
      />
    </div>
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
