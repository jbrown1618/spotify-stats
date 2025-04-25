import { Artist } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useAlbums } from "../useApi";
import { useSetFilters } from "../useFilters";
import { useIsMobile } from "../useIsMobile";

export function ArtistRow({ artist }: { artist: Artist }) {
  const isMobile = useIsMobile();
  const setFilters = useSetFilters();
  const { data: artistAlbums } = useAlbums({ artists: [artist.artist_uri] });

  const onClick = () =>
    setFilters({
      artists: [artist.artist_uri],
    });

  const highestRankedAlbum = artistAlbums
    ? Object.values(artistAlbums).sort(
        (a, b) => b.album_stream_count - a.album_stream_count
      )[0]
    : undefined;

  return (
    <RowDesign
      onClick={onClick}
      primaryText={artist.artist_name}
      itemURI={artist.artist_uri}
      src={artist.artist_image_url}
      secondarySrc={highestRankedAlbum?.album_image_url}
      stats={[
        { label: "Streams", value: artist.artist_stream_count ?? 0 },
        isMobile
          ? null
          : { label: "Popularity", value: artist.artist_popularity },
        isMobile
          ? null
          : {
              label: "Liked Tracks",
              value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
            },
      ]}
    />
  );
}
