import { Text } from "@mantine/core";

import { Album, Artist } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useSetFilters } from "../useFilters";
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
      itemURI={album.album_uri}
      tertiaryText={album.album_release_date}
      src={album.album_image_url}
      onClick={() =>
        setFilters({
          albums: [album.album_uri],
        })
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
        { label: "Streams", value: album.album_stream_count },
        isMobile
          ? null
          : {
              label: "Popularity",
              value: album.album_popularity,
            },
      ]}
    />
  );
}
