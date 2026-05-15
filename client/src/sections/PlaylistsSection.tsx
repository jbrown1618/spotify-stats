import { PlaylistsBarChart } from "../charts/PlaylistsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PlaylistRow } from "../list-items/PlaylistRow";
import { PlaylistTile } from "../list-items/PlaylistTile";
import { usePaginatedPlaylists } from "../useApi";
import { useFilters } from "../useFilters";

export function PlaylistsSection() {
  const filters = useFilters();
  if (filters.playlists?.length === 1) return null;
  return (
    <div>
      <h2>Playlists</h2>

      <PlaylistsBarChart />
      <PlaylistsDisplayGrid />
    </div>
  );
}

function PlaylistsDisplayGrid() {
  const { data, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    usePaginatedPlaylists();

  const items = data?.pages.flatMap((p) => p.items);
  const total = data?.pages[0]?.total ?? 0;

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(playlist) => playlist.playlist_uri}
      renderTile={(playlist) => <PlaylistTile playlist={playlist} />}
      renderRow={(playlist) => <PlaylistRow playlist={playlist} />}
      hasNextPage={hasNextPage}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
