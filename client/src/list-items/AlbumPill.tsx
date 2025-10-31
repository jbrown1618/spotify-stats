import { Album } from "../api";
import { PillWithAvatar } from "../design/PillDesign";
import { useSetFilters } from "../useFilters";

export function AlbumPill({ album }: { album: Album }) {
  const setFilters = useSetFilters();

  const onClick = () => {
    setFilters({ albums: [album.album_uri] });
  };
  return (
    <PillWithAvatar imageHref={album.album_image_url} onClick={onClick}>
      {album.album_short_name}
    </PillWithAvatar>
  );
}
