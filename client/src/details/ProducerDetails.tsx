import {
  Avatar,
  Badge,
  Group,
  Skeleton,
  Stack,
} from "@mantine/core";

import { KPIsList } from "../design/KPI";
import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists, useProducerProfile } from "../useApi";
import {
  DiscogsArtistCard,
  MusicBrainzArtistCard,
} from "./ArtistMetadataCards";
import styles from "./Details.module.css";

export function ProducerDetails({ producerKey }: { producerKey: string }) {
  const { data: producer } = useProducerProfile(producerKey);
  const { items: artists } = useArtists({
    filters: {
      artists: producer?.artist_uri ? [producer.artist_uri] : ["NO-ARTIST"],
    },
  });

  const artist = producer?.artist_uri
    ? artists?.find((a) => a.artist_uri === producer.artist_uri)
    : undefined;
  if (!producer) {
    return (
      <div className={styles.producerOverview}>
        <Skeleton circle h={160} w={160} />
        <Skeleton h={80} />
      </div>
    );
  }

  const discogsImage = producer.discogs_artists.find(
    (entry) => entry.primary_image_url
  )?.primary_image_url;

  return (
    <Stack gap="xl">
      <div className={styles.producerOverview}>
        {artist ? (
          <div className={styles.centered}>
            <ArtistTile large artist={artist} />
          </div>
        ) : (
          <Avatar
            src={producer.artist_image_url ?? discogsImage}
            name={producer.producer_name}
            size={160}
          />
        )}
        <KPIsList
          items={[
            { label: "Tracks", value: producer.track_count },
            {
              label: "Liked Tracks",
              value: `${producer.liked_track_count} / ${producer.track_count}`,
            },
            {
              label: "Credit Types",
              value: producer.credit_types.length,
            },
            { label: "Sources", value: producer.sources.length },
          ]}
        />
        <Group justify="center">
          {producer.credit_types.map((creditType) => (
            <Badge key={creditType} variant="light">
              {creditType}
            </Badge>
          ))}
        </Group>
      </div>

      {producer.musicbrainz_artists.map((entry) => (
        <MusicBrainzArtistCard key={entry.artist_mbid} artist={entry} />
      ))}
      {producer.discogs_artists.map((entry) => (
        <DiscogsArtistCard key={entry.discogs_artist_id} artist={entry} />
      ))}
    </Stack>
  );
}
