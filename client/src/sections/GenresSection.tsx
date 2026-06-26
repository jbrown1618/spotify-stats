import { Pill } from "@mantine/core";

import { GenresBarChart } from "../charts/GenresBarChart";
import { StreamShareAreaChart } from "../charts/StreamShareAreaChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PAGE_SIZE, useGenres, useGenresStreamShareByMonth } from "../useApi";
import { useSetFilters } from "../useFilters";
import styles from "./Sections.module.css";

export function GenresSection() {
  const { data: shareRows, shouldRender } = useGenresStreamShareByMonth();

  return (
    <div>
      <h2>Genres</h2>
      {shouldRender && (
        <StreamShareAreaChart
          rows={shareRows ?? []}
          title="Genre stream share over time"
          description="Monthly share for your current top 10 genres, with all other genres grouped as Other."
        />
      )}
      <GenresBarChart />
      <GenresDisplayGrid />
    </div>
  );
}

function GenresDisplayGrid() {
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useGenres({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(gtc) => gtc.genre}
      renderPill={(gtc) => <GenrePill genre={gtc.genre} />}
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}

function GenrePill({ genre }: { genre: string }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      className={styles.clickable}
      onClick={() => setFilters({ genres: [genre] })}
    >
      {genre}
    </Pill>
  );
}
