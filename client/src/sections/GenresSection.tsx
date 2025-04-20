import { Pill } from "@mantine/core";

import { GenresBarChart } from "../charts/GenresBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useGenres } from "../useApi";
import { useFilters, useSetFilters } from "../useFilters";

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
  const { data: genres } = useGenres();
  return (
    <DisplayGrid
      items={
        genres
          ? genres.sort(
              (a, b) => (b.liked_track_count ?? 0) - (a.liked_track_count ?? 0)
            )
          : undefined
      }
      getKey={(gtc) => gtc.genre}
      renderPill={(gtc) => <GenrePill genre={gtc.genre} />}
    />
  );
}

function GenrePill({ genre }: { genre: string }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      style={{ cursor: "pointer" }}
      onClick={() => setFilters({ genres: [genre] })}
    >
      {genre}
    </Pill>
  );
}
