import { PlaylistTile } from "../list-items/PlaylistTile";
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
        <PlaylistTile playlist={playlist} />
      </div>
    </>
  );
}
