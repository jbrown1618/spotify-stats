import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists, useProducers } from "../useApi";
import styles from "./Details.module.css";

export function ProducerDetails({ producerKey }: { producerKey: string }) {
  const { items: producers } = useProducers({
    filters: { producers: [producerKey] },
  });
  const producer = producers?.find((p) => p.producer_key === producerKey);
  const { items: artists } = useArtists({
    filters: { artists: producer?.artist_uri ? [producer.artist_uri] : [] },
  });
  if (!producers)
    return null;

  const artist = producer?.artist_uri
    ? artists?.find((a) => a.artist_uri === producer.artist_uri)
    : undefined;
  if (!producer) return null;

  return (
    <>
      {artist && (
        <div className={styles.centered}>
          <ArtistTile large artist={artist} />
        </div>
      )}
    </>
  );
}
