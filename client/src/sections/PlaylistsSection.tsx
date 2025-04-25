import { PlaylistsBarChart } from "../charts/PlaylistsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PlaylistTile } from "../list-items/PlaylistTile";
import { usePlaylists } from "../useApi";
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
  const { data: playlists, isLoading } = usePlaylists();
  return (
    <DisplayGrid
      loading={isLoading}
      items={
        playlists
          ? Object.values(playlists).sort(
              (a, b) =>
                b.playlist_liked_track_count - a.playlist_liked_track_count
            )
          : undefined
      }
      getKey={(playlist) => playlist.playlist_uri}
      renderTile={(playlist) => <PlaylistTile playlist={playlist} />}
    />
  );
}
