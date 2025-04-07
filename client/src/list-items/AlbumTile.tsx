import { useCallback } from "react";

import { Album } from "../api";
import { LargeTileDesign } from "../design/LargeTileDesign";
import { TileDesign } from "../design/TileDesign";
import { mostStreamedArtists } from "../sorting";
import { useArtists } from "../useApi";
import { useSetFilters } from "../useFilters";

interface AlbumTileProps {
  album: Album;
  large?: boolean;
}

export function AlbumTile({ album, large }: AlbumTileProps) {
  const setFilters = useSetFilters();
  const { data: artists } = useArtists({ albums: [album.album_uri] });

  const onClick = useCallback(
    () =>
      setFilters({
        albums: [album.album_uri],
      }),
    [album.album_uri, setFilters]
  );

  if (!large) {
    return (
      <TileDesign
        title={album.album_short_name}
        src={album.album_image_url}
        onClick={onClick}
        itemURI={album.album_uri}
        stats={[
          { label: "Rank", value: album.album_rank },
          { label: "Streams", value: album.album_stream_count },
        ]}
      />
    );
  }

  const artist = artists
    ? Object.values(artists).sort(mostStreamedArtists)[0]
    : undefined;

  return (
    <LargeTileDesign
      title={album.album_name}
      subtitle={album.album_label}
      src={album.album_image_url}
      secondarySrc={artist?.artist_image_url}
      onClick={onClick}
      itemURI={album.album_uri}
      stats={[
        { label: "Rank", value: album.album_rank },
        { label: "Streams", value: album.album_stream_count },
        { label: "Popularity", value: album.album_popularity },
        { label: "Release date", value: album.album_release_date },
      ]}
    />
  );
}
