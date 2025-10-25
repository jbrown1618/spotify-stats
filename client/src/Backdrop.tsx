import { Track } from "./api";
import styles from "./Backdrop.module.css";
import { mostStreamedTracks } from "./sorting";
import { useTracks } from "./useApi";

export function Backdrop() {
  return (
    <div className={styles.backdrop}>
      <HeaderBackdrop />
      <AlbumTiles />
    </div>
  );
}

function HeaderBackdrop() {
  return <div className={styles.headerBackground} />;
}

function AlbumTiles() {
  const tiles = useAlbumTiles();
  return tiles && tiles.length > 0 ? (
    tiles.length >= 4 ? (
      <AlbumTilesDesign tiles={tiles} />
    ) : (
      <SingleAlbumTileDesign tile={tiles[0]} />
    )
  ) : null;
}

function AlbumTilesDesign({ tiles }: { tiles: Tile[] }) {
  return (
    <div
      className={styles.tileContainer}
      key={tiles
        .slice(10)
        .map((t) => t.key)
        .join("-")}
    >
      {tiles.map((tile) => (
        <AlbumTile key={tile.key} href={tile.href} />
      ))}
    </div>
  );
}

function SingleAlbumTileDesign({ tile }: { tile: Tile }) {
  return (
    <div className={styles.singleTileContainer} key={tile.key}>
      <div
        className={styles.singleTile}
        style={{
          backgroundImage: `url(${tile.href})`,
        }}
      />
    </div>
  );
}

function AlbumTile({ href }: { href: string }) {
  return (
    <div
      className={styles.tile}
      style={{
        backgroundImage: `url(${href})`,
      }}
    />
  );
}

const maxItems = 100;

interface Tile {
  href: string;
  key: string;
}

function useAlbumTiles(): Tile[] | null {
  const { data: tracks } = useTracks();
  if (!tracks) return null;

  const tiles = deduplicateBy(
    Object.values(tracks).sort(mostStreamedTracks).map(toTile),
    "href"
  );

  if (tiles.length === 0) {
    return null;
  }

  if (tiles.length < 4) {
    return [tiles[0]];
  }

  // If we have enough albums, just slice to maxItems
  if (tiles.length >= maxItems) {
    return tiles.slice(0, maxItems);
  }

  // If fewer than maxItems albums, repeat items until we have maxItems
  const result = [];
  while (result.length < maxItems) {
    for (let i = 0; i < tiles.length && result.length < maxItems; i++) {
      result.push({ key: `${tiles[i].key}-${i}`, href: tiles[i].href });
    }
  }

  return result;
}

const prefixLength = "spotify:track".length;

function toTile(track: Track): Tile {
  return {
    key: track.track_uri.slice(prefixLength + 1),
    href: track.album_image_url,
  };
}

function deduplicateBy<T, K extends keyof T>(array: T[], key: K): T[] {
  const seen = new Set();
  return array.filter((item) => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
}
