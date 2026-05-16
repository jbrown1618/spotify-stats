import { Pill } from "@mantine/core";

import { YearsBarChart } from "../charts/YearsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useReleaseYears, PAGE_SIZE } from "../useApi";
import { useSetFilters } from "../useFilters";
import styles from "./Sections.module.css";

export function ReleaseYearsSection() {
  return (
    <div>
      <h2>Release date</h2>

      <YearsBarChart />
      <YearsDisplayGrid />
    </div>
  );
}

function YearsDisplayGrid() {
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useReleaseYears({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(yc) => "" + yc.release_year}
      renderPill={(yc) => <ReleaseYearPill year={yc.release_year} />}
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}

function ReleaseYearPill({ year }: { year: number }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      className={styles.clickable}
      onClick={() => setFilters({ years: [year] })}
    >
      {year}
    </Pill>
  );
}
