import { Pill } from "@mantine/core";

import { GenresBarChart } from "../charts/GenresBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useGenres, PAGE_SIZE } from "../useApi";
import { useFilters, useSetFilters } from "../useFilters";
import styles from "./Sections.module.css";

export function GenresSection() {
  const filters = useFilters();
  if (filters.genres?.length === 1) return null;
  return (
    <div>
      <h2>Genres</h2>
      <GenresBarChart />
      <GenresDisplayGrid />
    </div>
  );
}

function GenresDisplayGrid() {
  const { items, total, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    useGenres({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(gtc) => gtc.genre}
      renderPill={(gtc) => <GenrePill genre={gtc.genre} />}
      hasNextPage={hasNextPage}
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
