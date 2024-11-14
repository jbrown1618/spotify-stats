import { Album } from "./api";
import { useSetFilters } from "./useSetFilters";
import { TileDesign } from "./TileDesign";

interface AlbumTileProps {
  album: Album;
}

export function AlbumTile({ album }: AlbumTileProps) {
  const setFilters = useSetFilters();
  return (
    <TileDesign
      title={album.album_name}
      src={album.album_image_url}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          albums: [album.album_uri],
        }))
      }
    />
  );
}
