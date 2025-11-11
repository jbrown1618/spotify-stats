import { Playlist } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useSetFilters } from "../useFilters";

export function PlaylistRow({ playlist }: { playlist: Playlist }) {
  const setFilters = useSetFilters();

  const onClick = () =>
    setFilters({
      playlists: [playlist.playlist_uri],
    });

  return (
    <RowDesign
      onClick={onClick}
      primaryText={playlist.playlist_name}
      itemURI={playlist.playlist_uri}
      src={playlist.playlist_image_url}
      stats={[
        { label: "Tracks", value: playlist.playlist_track_count },
        { label: "Liked", value: playlist.playlist_liked_track_count },
      ]}
    />
  );
}
