import { Playlist } from "../api";
import { useSetFilters } from "../useSetFilters";
import { TileDesign } from "../design/TileDesign";

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
        setFilters((filters) => ({
          ...filters,
          playlists: [playlist.playlist_uri],
        }))
      }
    />
  );
}
