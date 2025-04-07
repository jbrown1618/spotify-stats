import { Skeleton } from "@mantine/core";

import { Artist } from "../api";
import { LargeTileDesign } from "../design/LargeTileDesign";
import { TileDesign } from "../design/TileDesign";
import { useAlbums } from "../useApi";
import { useSetFilters } from "../useFilters";

interface ArtistTileProps {
  artist: Artist;
  large?: boolean;
}

export function ArtistTile({ artist, large }: ArtistTileProps) {
  const setFilters = useSetFilters();
  const { data: artistAlbums } = useAlbums({ artists: [artist.artist_uri] });

  const onClick = () =>
    setFilters({
      artists: [artist.artist_uri],
    });

  if (!large)
    return (
      <TileDesign
        title={artist.artist_name}
        src={artist.artist_image_url}
        onClick={onClick}
        itemURI={artist.artist_uri}
        stats={[
          { label: "Rank", value: artist.artist_rank },
          { label: "Streams", value: artist.artist_stream_count },
        ]}
      />
    );

  const highestRankedAlbum = artistAlbums
    ? Object.values(artistAlbums).sort(
        (a, b) => b.album_stream_count - a.album_stream_count
      )[0]
    : undefined;

  return (
    <LargeTileDesign
      title={artist.artist_name}
      src={artist.artist_image_url}
      secondarySrc={highestRankedAlbum?.album_image_url}
      itemURI={artist.artist_uri}
      onClick={onClick}
      stats={[
        { label: "Rank", value: artist.artist_rank },
        { label: "Streams", value: artist.artist_stream_count },
        { label: "Popularity", value: artist.artist_popularity },
        {
          label: "Liked Tracks",
          value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
        },
        {
          label: "Albums",
          value: artistAlbums ? (
            Object.keys(artistAlbums).length
          ) : (
            <Skeleton height={24} width={24} />
          ),
        },
      ]}
    />
  );
}
