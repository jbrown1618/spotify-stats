import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { KPIsList } from "../design/KPI";
import { useAlbums } from "../useApi";
import styles from "./Details.module.css";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { data: albums } = useAlbums({ albums: [albumURI] });

  if (!albums) return null; // TODO: skeleton

  const album = albums[albumURI];
  if (!album) return null;

  return (
    <>
      <h2>{album.album_name}</h2>

      <div className={styles.centered}>
        <KPIsList
          items={[
            { label: "Streams", value: album.album_stream_count ?? 0 },
            { label: "Popularity", value: album.album_popularity },
            { label: "Release date", value: album.album_release_date },
          ]}
        />
      </div>
      <AlbumsStreamingHistoryStack />
      <AlbumStreamsLineChart height={300} />
    </>
  );
}
