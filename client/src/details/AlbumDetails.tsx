import { Anchor, Badge, Group, Paper, Stack, Table, Text } from "@mantine/core";

import {
  AlbumTrackMetadata,
  DiscogsMasterMetadata,
} from "../api";
import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { ArtistPills } from "../design/ArtistPills";
import { KPIsList } from "../design/KPI";
import { TextSkeleton } from "../design/TextSkeleton";
import { useAlbumMetadata, useAlbums } from "../useApi";
import styles from "./Details.module.css";

interface AlbumDetailsProps {
  albumURI: string;
}

export function AlbumDetails({ albumURI }: AlbumDetailsProps) {
  const { items: albums } = useAlbums({ filters: { albums: [albumURI] } });
  const { data: metadata } = useAlbumMetadata(albumURI);

  const album = albums?.find((a) => a.album_uri === albumURI);

  return (
    <>
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
      {metadata && (
        <AlbumSourceMetadata
          masters={metadata.discogs_masters}
          tracks={metadata.tracks}
        />
      )}
      <AlbumsStreamingHistoryStack />
      <AlbumStreamsLineChart height={300} />
    </>
  );
}

function AlbumSourceMetadata({
  masters,
  tracks,
}: {
  masters: DiscogsMasterMetadata[];
  tracks: AlbumTrackMetadata[];
}) {
  if (masters.length === 0 && tracks.length === 0) return null;

  const tracksByUri = Object.values(
    tracks.reduce<Record<string, AlbumTrackMetadata[]>>((grouped, track) => {
      grouped[track.track_uri] = [...(grouped[track.track_uri] ?? []), track];
      return grouped;
    }, {}),
  );

  return (
    <Stack gap="lg" mt="xl">
      {masters.map((master) => (
        <Paper key={master.discogs_master_id} withBorder p="lg" radius="md">
          <Group justify="space-between">
            <Text fw={600} size="lg">
              {master.title}
              {master.year ? ` (${master.year})` : ""}
            </Text>
            <Anchor
              href={`https://www.discogs.com/master/${master.discogs_master_id}`}
              target="_blank"
              rel="noreferrer"
            >
              Discogs
            </Anchor>
          </Group>
          <Group gap="xs" mt="sm">
            {[
              ...master.genres,
              ...master.styles,
              ...master.formats,
              ...master.countries,
            ].map((value) => (
              <Badge key={value} variant="light">
                {value}
              </Badge>
            ))}
          </Group>
          {master.labels.length > 0 && (
            <Text mt="sm">
              <strong>Labels:</strong> {master.labels.join(", ")}
            </Text>
          )}
        </Paper>
      ))}

      {tracksByUri.length > 0 && (
        <Table.ScrollContainer minWidth={600}>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Track</Table.Th>
                <Table.Th>Source</Table.Th>
                <Table.Th>Source title</Table.Th>
                <Table.Th>Details</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {tracksByUri.flatMap((sourceTracks) =>
                sourceTracks.map((track) => (
                  <Table.Tr
                    key={`${track.track_uri}-${track.source}-${track.source_id}`}
                  >
                    <Table.Td>{track.track_name}</Table.Td>
                    <Table.Td>
                      <Anchor
                        href={
                          track.source === "musicbrainz"
                            ? `https://musicbrainz.org/recording/${track.source_id}`
                            : `https://www.discogs.com/master/${track.source_id}`
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        {track.source === "musicbrainz"
                          ? "MusicBrainz"
                          : "Discogs"}
                      </Anchor>
                    </Table.Td>
                    <Table.Td>{track.source_title}</Table.Td>
                    <Table.Td>
                      {track.position
                        ? `Position ${track.position}`
                        : track.language?.toUpperCase() || "-"}
                    </Table.Td>
                  </Table.Tr>
                )),
              )}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      )}
    </Stack>
  );
}
