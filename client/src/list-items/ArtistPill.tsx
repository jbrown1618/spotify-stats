import { Artist } from "../api";
import { PillWithAvatar } from "../design/PillDesign";
import { useSetFilters } from "../useFilters";

export function ArtistPill({ artist }: { artist: Artist }) {
  const setFilters = useSetFilters();

  const onClick = () => {
    setFilters({ artists: [artist.artist_uri] });
  };
  return (
    <PillWithAvatar imageHref={artist.artist_image_url} onClick={onClick}>
      {artist.artist_name}
    </PillWithAvatar>
  );
}
