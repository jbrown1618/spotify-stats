import { Playlist } from "../api";
import { TileDesign } from "../design/TileDesign";
import { useSetFilters } from "../useFilters";

interface PlaylistTileProps {
  playlist: Playlist;
}

export function PlaylistTile({ playlist }: PlaylistTileProps) {
  const setFilters = useSetFilters();
  return (
    <TileDesign
      title={playlist.playlist_name}
      src={playlist.playlist_image_url}
      onClick={() =>
        setFilters({
          playlists: [playlist.playlist_uri],
        })
      }
    />
  );
}
