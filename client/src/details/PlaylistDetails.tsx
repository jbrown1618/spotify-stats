import { KPIsList } from "../design/KPI";
import { usePlaylists } from "../useApi";

export function PlaylistDetails({ playlistURI }: { playlistURI: string }) {
  const { data: playlists } = usePlaylists({ playlists: [playlistURI] });
  if (!playlists) return null;

  const playlist = playlists[playlistURI];
  if (!playlist) return null;

  return (
    <>
      <h2>{playlist.playlist_name}</h2>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <KPIsList
          items={[
            { label: "Tracks", value: playlist.playlist_track_count },
            { label: "Liked", value: playlist.playlist_liked_track_count },
          ]}
        />
      </div>
    </>
  );
}
