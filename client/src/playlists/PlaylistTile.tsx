import { Playlist } from "../api";
import { useSetFilters } from "../useFilters";
import { TileDesign } from "../design/TileDesign";

interface PlaylistTileProps {
  playlist: Playlist;
  playlist_images: Record<string, string[]>;
}

export function PlaylistTile({ playlist, playlist_images }: PlaylistTileProps) {
  const setFilters = useSetFilters();
  return (
    <TileDesign
      title={playlist.playlist_name}
      src={
        playlist.playlist_image_url ?? playlist_images[playlist.playlist_uri]
      }
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          playlists: [playlist.playlist_uri],
        }))
      }
    />
  );
}
