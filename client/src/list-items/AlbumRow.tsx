import { Skeleton, Text } from "@mantine/core";
import { Fragment } from "react/jsx-runtime";

import { Album } from "../api";
import { RowDesign } from "../design/RowDesign";
import { mostStreamedArtists } from "../sorting";
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
        { label: "Streams", value: album.album_stream_count ?? 0 },
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

  if (!albumArtists)
    return (
      <div
        style={{
          height: 24,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <Skeleton width={100} height={14} />
      </div>
    );

  return (
    <div style={{ display: "flex" }}>
      {Object.values(albumArtists)
        .sort(mostStreamedArtists)
        .map((artist, i) => {
          return (
            <Fragment key={artist.artist_uri}>
              <Text>{artist.artist_name}</Text>
              {i < Object.values(albumArtists).length - 1 ? (
                <Text>,&nbsp;</Text>
              ) : null}
            </Fragment>
          );
        })}
    </div>
  );
}
