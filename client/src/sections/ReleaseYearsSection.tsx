import { Pill } from "@mantine/core";

import { YearsBarChart } from "../charts/YearsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useReleaseYears } from "../useApi";
import { useSetFilters } from "../useFilters";

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
  const { data: years } = useReleaseYears();
  return (
    <DisplayGrid
      items={
        years
          ? Object.values(years).sort(
              (a, b) => (b.liked_track_count ?? 0) - (a.liked_track_count ?? 0)
            )
          : undefined
      }
      getKey={(yc) => "" + yc.release_year}
      renderPill={(yc) => <ReleaseYearPill year={yc.release_year} />}
    />
  );
}

function ReleaseYearPill({ year }: { year: number }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      style={{ cursor: "pointer" }}
      onClick={() => setFilters({ years: [year] })}
    >
      {year}
    </Pill>
  );
}
