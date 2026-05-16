import { PlaylistsBarChart } from "../charts/PlaylistsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PlaylistRow } from "../list-items/PlaylistRow";
import { PlaylistTile } from "../list-items/PlaylistTile";
import { usePlaylists, PAGE_SIZE } from "../useApi";
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
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    usePlaylists({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(playlist) => playlist.playlist_uri}
      renderTile={(playlist) => <PlaylistTile playlist={playlist} />}
      renderRow={(playlist) => <PlaylistRow playlist={playlist} />}
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
