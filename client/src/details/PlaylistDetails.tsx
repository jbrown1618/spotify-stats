import { PlaylistTile } from "../list-items/PlaylistTile";
import { usePlaylists } from "../useApi";
import styles from "./PlaylistDetails.module.css";

export function PlaylistDetails({ playlistURI }: { playlistURI: string }) {
  const { data: playlists } = usePlaylists({ playlists: [playlistURI] });
  if (!playlists) return null;

  const playlist = playlists[playlistURI];
  if (!playlist) return null;

  return (
    <>
      <h2>{playlist.playlist_name}</h2>
      <div className={styles.centeredContainer}>
        <PlaylistTile playlist={playlist} />
      </div>
    </>
  );
}
