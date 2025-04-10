import { PlaylistsBarChart } from "../charts/PlaylistsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PlaylistTile } from "../list-items/PlaylistTile";
import { usePlaylists } from "../useApi";

export function PlaylistsSection() {
  return (
    <div>
      <h2>Playlists</h2>

      <PlaylistsBarChart />
      <PlaylistsDisplayGrid />
    </div>
  );
}

function PlaylistsDisplayGrid() {
  const { data: playlists } = usePlaylists();
  return (
    <DisplayGrid
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
