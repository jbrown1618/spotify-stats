import { Album } from "../api";
import { LargeTileDesign } from "../design/LargeTileDesign";
import { TileDesign } from "../design/TileDesign";
import { useSetFilters } from "../useFilters";
import { useSummary } from "../useSummary";

interface AlbumTileProps {
  album: Album;
  large?: boolean;
}

export function AlbumTile({ album, large }: AlbumTileProps) {
  const { data: summary } = useSummary();
  const setFilters = useSetFilters();

  if (large) {
    const artist =
      summary?.artists[summary?.artists_by_album[album.album_uri][0]];
    return (
      <LargeTileDesign
        title={album.album_name}
        subtitle={album.album_label}
        src={album.album_image_url}
        secondarySrc={artist?.artist_image_url}
        onClick={() =>
          setFilters({
            albums: [album.album_uri],
          })
        }
        stats={[
          { label: "Rank", value: album.album_rank },
          { label: "Streams", value: album.album_stream_count },
          { label: "Popularity", value: album.album_popularity },
          { label: "Release date", value: album.album_release_date },
        ]}
      />
    );
  }
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
