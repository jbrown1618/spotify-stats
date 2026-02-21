import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { ArtistPills } from "../design/ArtistPills";
import { KPIsList } from "../design/KPI";
import { TextSkeleton } from "../design/TextSkeleton";
import { useAlbums } from "../useApi";
import styles from "./Details.module.css";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { data: albums } = useAlbums({ albums: [albumURI] });

  const album = albums?.[albumURI];

  return (
    <>
      {album ? <h2>{album.album_name}</h2> : <TextSkeleton style="h2" />}

      <div className={styles.centered}>
        <KPIsList
          items={[
            {
              label: "Artist",
              value: <ArtistPills filters={{ albums: [albumURI] }} />,
            },
            {
              label: "Streams",
              value: album ? (
                (album.album_stream_count ?? 0)
              ) : (
                <TextSkeleton style="regular" />
              ),
            },
            {
              label: "Popularity",
              value: album ? (
                album.album_popularity
              ) : (
                <TextSkeleton style="regular" />
              ),
            },
            {
              label: "Release date",
              value: album ? (
                album.album_release_date
              ) : (
                <TextSkeleton style="regular" />
              ),
            },
          ]}
        />
      </div>
      <AlbumsStreamingHistoryStack />
      <AlbumStreamsLineChart height={300} />
    </>
  );
}
