import { Skeleton, Text } from "@mantine/core";

import { Album } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useArtists } from "../useApi";
import { useSetFilters } from "../useFilters";
import { useIsMobile } from "../useIsMobile";

interface AlbumTileProps {
  album: Album;
}

export function AlbumRow({ album }: AlbumTileProps) {
  const isMobile = useIsMobile();
  const setFilters = useSetFilters();
  return (
    <RowDesign
      primaryText={isMobile ? album.album_short_name : album.album_name}
      itemURI={album.album_uri}
      tertiaryText={album.album_release_date}
      src={album.album_image_url}
      onClick={() =>
        setFilters({
          albums: [album.album_uri],
        })
      }
      secondaryText={<ArtistsList albumURI={album.album_uri} />}
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

function ArtistsList({ albumURI }: { albumURI: string }) {
  const { data: albumArtists } = useArtists({ albums: [albumURI] });

  if (!albumArtists) return <Skeleton width={100} height={12} />;

  return (
    <>
      {Object.values(albumArtists).map((artist) => {
        return <Text>{artist.artist_name}</Text>;
      })}
    </>
  );
}
