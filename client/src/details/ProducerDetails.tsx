import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists, useProducers } from "../useApi";
import styles from "./Details.module.css";

export function ProducerDetails({ mbid }: { mbid: string }) {
  const { items: producers } = useProducers({ filters: { producers: [mbid] } });
  const producer = producers?.find((p) => p.producer_mbid === mbid);
  const { items: artists } = useArtists({
    filters: { artists: producer?.artist_uri ? [producer.artist_uri] : [] },
  });
  if (!producers) return null;

  const artist = producer?.artist_uri
    ? artists?.find((a) => a.artist_uri === producer.artist_uri)
    : undefined;
  if (!producer) return null;

  return (
    <>
      <h2>{producer.producer_name}</h2>
      {artist && (
        <div className={styles.centered}>
          <ArtistTile large artist={artist} />
        </div>
      )}
    </>
  );
}
