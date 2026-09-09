import { Pill } from "@mantine/core";
import { useState } from "react";

import { YearsBarChart } from "../charts/YearsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PAGE_SIZE, useReleaseYears } from "../useApi";
import { useSetFilters } from "../useFilters";
import { SectionHeading } from "./SectionHeading";
import styles from "./Sections.module.css";

const yearSortOptions = ["Newest", "Oldest", "Most liked tracks"];

export function ReleaseYearsSection() {
  const [sort, setSort] = useState("Newest");
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useReleaseYears({ sort, limit: PAGE_SIZE });

  return (
    <div>
      <SectionHeading title="Release date" total={total} />

      <YearsBarChart />
      <DisplayGrid
        loading={isLoading}
        items={items}
        total={total}
        sortOptions={yearSortOptions}
        sort={sort}
        onSortChange={setSort}
        getKey={(yc) => "" + yc.release_year}
        renderPill={(yc) => <ReleaseYearPill year={yc.release_year} />}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={() => fetchNextPage()}
      />
    </div>
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
