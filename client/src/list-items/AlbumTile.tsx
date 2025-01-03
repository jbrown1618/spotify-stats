import { Album } from "../api";
import { TileDesign } from "../design/TileDesign";
import { useSetFilters } from "../FiltersProvider";

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
        setFilters({
          albums: [album.album_uri],
        })
      }
    />
  );
}
