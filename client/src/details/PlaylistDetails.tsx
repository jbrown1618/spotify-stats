import { KPIsList, KPIsListSkeleton } from "../design/KPI";
import { TextSkeleton } from "../design/TextSkeleton";
import { usePlaylists } from "../useApi";
import styles from "./Details.module.css";

export function PlaylistDetails({ playlistURI }: { playlistURI: string }) {
  const { items: playlists } = usePlaylists({ filters: { playlists: [playlistURI] } });
  if (!playlists)
    return (
      <>
        <TextSkeleton style="h2" />
        <div className={styles.centered}>
          <KPIsListSkeleton count={2} />
        </div>
      </>
    );

  const playlist = playlists.find((p) => p.playlist_uri === playlistURI);
  if (!playlist) return null;

  return (
    <>
      <h2>{playlist.playlist_name}</h2>
      <div className={styles.centered}>
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
