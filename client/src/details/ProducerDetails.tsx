import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists, useProducers } from "../useApi";

export function ProducerDetails({ mbid }: { mbid: string }) {
  const { data: producers } = useProducers({ producers: [mbid] });
  const { data: artists } = useArtists({
    artists: producers?.[mbid].artist_uri ? [producers?.[mbid].artist_uri] : [],
  });
  if (!producers) return null;

  const producer = producers[mbid];
  const artist = producer?.artist_uri
    ? artists?.[producer.artist_uri]
    : undefined;
  if (!producer) return null;

  return (
    <>
      <h2>{producer.producer_name}</h2>
      {artist && (
        <div style={{ display: "flex", justifyContent: "center" }}>
          <ArtistTile large artist={artist} />
        </div>
      )}
    </>
  );
}
