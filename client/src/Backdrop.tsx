import styles from "./Backdrop.module.css";
import { mostStreamedAlbums } from "./sorting";
import { useAlbums } from "./useApi";

export function Backdrop() {
  const albumTiles = useAlbumTiles();
  return (
    <div className={styles.backdrop}>
      <HeaderBackdrop />
      {albumTiles && (
        <div className={styles.tileContainer}>
          {albumTiles.map((album) => (
            <div
              key={album.album_uri}
              className={styles.tile}
              style={{
                backgroundImage: `url(${album.album_image_url})`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function HeaderBackdrop() {
  return <div className={styles.headerBackground} />;
}

const maxItems = 100;

function useAlbumTiles() {
  const { data: albums } = useAlbums();
  if (!albums) return null;

  const sortedAlbums = Object.values(albums).sort(mostStreamedAlbums);

  // Return null if fewer than 3 albums
  if (sortedAlbums.length < 3) return null;

  // If we have enough albums, just slice to maxItems
  if (sortedAlbums.length >= maxItems) {
    return sortedAlbums.slice(0, maxItems);
  }

  // If fewer than maxItems albums, repeat items until we have maxItems
  const result = [];
  while (result.length < maxItems) {
    for (let i = 0; i < sortedAlbums.length && result.length < maxItems; i++) {
      result.push(sortedAlbums[i]);
    }
  }

  return result;
}
