import { Text } from "@mantine/core";
import { Album, Artist } from "../api";
import { useSetFilters } from "../useFilters";
import { RowDesign } from "../design/RowDesign";
import { useIsMobile } from "../useIsMobile";

interface AlbumTileProps {
  album: Album;
  artists_by_album: Record<string, string[]>;
  artists: Record<string, Artist>;
}

export function AlbumRow({ album, artists_by_album, artists }: AlbumTileProps) {
  const isMobile = useIsMobile();
  const setFilters = useSetFilters();
  return (
    <RowDesign
      primaryText={album.album_name}
      tertiaryText={album.album_release_date}
      src={album.album_image_url}
      onClick={() =>
        setFilters((filters) => ({
          ...filters,
          albums: [album.album_uri],
        }))
      }
      secondaryText={
        <>
          {artists_by_album[album.album_uri].map((artistURI) => {
            const artist = artists[artistURI];
            if (!artist) return null;

            return <Text>{artist.artist_name}</Text>;
          })}
        </>
      }
      stats={[
        { label: "Rank", value: album.album_rank },
        isMobile
          ? null
          : {
              label: "Popularity",
              value: album.album_popularity,
            },
        {
          label: "Tracks",
          value: album.album_total_tracks,
        },
      ]}
    />
  );
}
