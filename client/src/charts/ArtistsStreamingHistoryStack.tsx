import { useState } from "react";

import { Artist } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";
import styles from "./StreamingHistoryItem.module.css";

export function ArtistsStreamingHistoryStack({
  onlyArtist,
}: {
  onlyArtist?: string;
}) {
  const [n, setN] = useState(5);
  const { data: artists } = useArtists();
  const { data: history, shouldRender } = useArtistsStreamsByMonth(n);

  if (!artists || !history) return <ChartSkeleton />;

  if (!shouldRender) return null;

  const data = onlyArtist
    ? Object.fromEntries(
        Object.entries(history).filter(
          ([artistUri]) => artistUri === onlyArtist
        )
      )
    : history;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={data}
        getItem={(key) => artists[key]}
        sortItems={mostStreamedArtists}
        onMore={
          n < Object.keys(artists).length
            ? () => setN((prev) => prev + 5)
            : undefined
        }
        onLess={n > 5 ? () => setN(5) : undefined}
        renderItem={(artist: Artist) => (
          <h4 className={styles.itemHeading}>
            <img className={styles.itemImage} src={artist.artist_image_url} />
            {artist.artist_name}
          </h4>
        )}
      />
    </>
  );
}
