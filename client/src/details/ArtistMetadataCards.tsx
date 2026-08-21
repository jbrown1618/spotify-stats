import {
  Anchor,
  Avatar,
  Badge,
  Group,
  Paper,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import {
  DiscogsArtistMetadata,
  MusicBrainzArtistMetadata,
} from "../api";
import styles from "./Details.module.css";

export function MusicBrainzArtistCard({
  artist,
}: {
  artist: MusicBrainzArtistMetadata;
}) {
  const activeYears = [artist.start_date, artist.end_date]
    .filter(Boolean)
    .join(" - ");

  return (
    <Paper withBorder p="lg" radius="md">
      <Stack gap="sm">
        <Group justify="space-between">
          <Title order={3}>{artist.name}</Title>
          <Anchor
            href={`https://musicbrainz.org/artist/${artist.artist_mbid}`}
            target="_blank"
            rel="noreferrer"
          >
            MusicBrainz
          </Anchor>
        </Group>
        {artist.disambiguation && (
          <Text c="dimmed">{artist.disambiguation}</Text>
        )}
        <Group gap="xs">
          {[artist.type, artist.gender, artist.area, activeYears]
            .filter(Boolean)
            .map((detail) => (
              <Badge key={detail} variant="outline">
                {detail}
              </Badge>
            ))}
        </Group>
        {artist.birthplace && (
          <Text>
            <strong>Born in:</strong> {artist.birthplace}
          </Text>
        )}
        {artist.aliases.length > 0 && (
          <Text>
            <strong>Also known as:</strong> {artist.aliases.join(", ")}
          </Text>
        )}
      </Stack>
    </Paper>
  );
}

export function DiscogsArtistCard({
  artist,
}: {
  artist: DiscogsArtistMetadata;
}) {
  return (
    <Paper withBorder p="lg" radius="md">
      <Group align="flex-start" wrap="nowrap">
        {artist.primary_image_url && (
          <Avatar
            src={artist.primary_image_url}
            name={artist.name}
            size={96}
          />
        )}
        <Stack gap="sm" className={styles.sourceContent}>
          <Group justify="space-between">
            <Title order={3}>{artist.name}</Title>
            <Anchor
              href={`https://www.discogs.com/artist/${artist.discogs_artist_id}`}
              target="_blank"
              rel="noreferrer"
            >
              Discogs
            </Anchor>
          </Group>
          {artist.realname && (
            <Text>
              <strong>Real name:</strong> {artist.realname}
            </Text>
          )}
          {artist.namevariations.length > 0 && (
            <Text>
              <strong>Name variations:</strong>{" "}
              {artist.namevariations.join(", ")}
            </Text>
          )}
          {artist.profile && (
            <Text className={styles.sourceProfile}>{artist.profile}</Text>
          )}
        </Stack>
      </Group>
    </Paper>
  );
}
