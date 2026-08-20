import { Anchor, Group, Paper, Stack, Text, Title } from "@mantine/core";
import {
  IconBrandYoutube,
  IconHeart,
  IconHeartFilled,
} from "@tabler/icons-react";
import clsx from "clsx";

import type { Credit } from "../api";
import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { ArtistPills } from "../design/ArtistPills";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { KPIsList, KPIsListSkeleton } from "../design/KPI";
import { AlbumPill } from "../list-items/AlbumPill";
import { ArtistPill } from "../list-items/ArtistPill";
import sharedStyles from "../list-items/ListItems.module.css";
import { useTrackCredits, useTracks, useTrackVideos } from "../useApi";
import { formatDate } from "../utils";
import styles from "./Details.module.css";

export function TrackDetails({ trackURI }: { trackURI: string }) {
  const { items: tracks } = useTracks({ filters: { tracks: [trackURI] } });
  const track = tracks?.[0];
  const { data: credits } = useTrackCredits(trackURI);
  const { data: videos } = useTrackVideos(trackURI);

  if (!track)
    return (
      <>
        <div className={styles.centered}>
          <KPIsListSkeleton count={7} />
        </div>
        <ChartSkeleton />
      </>
    );

  return (
    <>
      <div className={styles.centered}>
        <KPIsList
          items={[
            { label: "Album", value: <AlbumPill album={track} /> },
            {
              label: track.artist_names.length > 1 ? "Artists" : "Artist",
              value: <ArtistPills filters={{ tracks: [trackURI] }} />,
            },
            {
              label: "Release date",
              value: track.album_release_date || "Unknown",
            },
            { label: "Streams", value: track.track_stream_count ?? 0 },
            {
              label: "Last played",
              value: track.track_last_played_at
                ? formatDate(new Date(track.track_last_played_at))
                : "Never",
            },
            { label: "Popularity", value: track.track_popularity },
            {
              label: "Liked",
              value: track.track_liked ? (
                <IconHeartFilled
                  title="Liked"
                  className={clsx(
                    sharedStyles.likedIcon,
                    sharedStyles.likedIconGreen,
                  )}
                />
              ) : (
                <IconHeart
                  title="Liked"
                  className={clsx(
                    sharedStyles.likedIcon,
                    sharedStyles.likedIconGray,
                  )}
                />
              ),
            },
          ]}
        />
      </div>
      {videos && videos.length > 0 && <TrackVideos videos={videos} />}
      {credits && credits.length > 0 && <Credits credits={credits} />}
      <TracksStreamingHistoryStack />
      <TrackStreamsLineChart height={300} />
    </>
  );
}

function TrackVideos({
  videos,
}: {
  videos: {
    uri: string;
    title: string | null;
    duration_seconds: number | null;
  }[];
}) {
  return (
    <Paper withBorder p="lg" radius="md" mt="xl">
      <Stack gap="sm">
        <Title order={3}>Videos</Title>
        {videos.map((video) => (
          <Group key={video.uri} gap="sm">
            <IconBrandYoutube color="var(--mantine-color-red-6)" />
            <Anchor href={video.uri} target="_blank" rel="noreferrer">
              {video.title || "Watch on YouTube"}
            </Anchor>
            {video.duration_seconds && (
              <Text c="dimmed" size="sm">
                {formatDuration(video.duration_seconds)}
              </Text>
            )}
          </Group>
        ))}
      </Stack>
    </Paper>
  );
}

function formatDuration(durationSeconds: number) {
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = durationSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function Credits({ credits }: { credits: Credit[] }) {
  const creditsByType = credits.reduce(
    (acc, credit) => {
      acc[credit.credit_type] = [...(acc[credit.credit_type] ?? []), credit];
      return acc;
    },
    {} as Record<string, Credit[]>,
  );

  const creditTypeOrder = [
    "producer",
    "songwriter",
    "lyricist",
    "arranger",
    "sound",
    "mastering",
    "audio director",
    "video director",
    "publishing",
  ];
  const sortedCreditTypes = Object.entries(creditsByType).sort(
    ([typeA], [typeB]) => {
      const indexA = creditTypeOrder.indexOf(typeA);
      const indexB = creditTypeOrder.indexOf(typeB);
      if (indexA === -1 && indexB === -1) return typeA.localeCompare(typeB);
      if (indexA === -1) return 1;
      if (indexB === -1) return -1;
      return indexA - indexB;
    },
  );

  return (
    <div style={{ marginTop: 32, marginBottom: 32 }}>
      <h3 style={{ marginBottom: 16 }}>Credits</h3>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr
            style={{
              borderBottom: "1px solid var(--mantine-color-default-border)",
              textAlign: "left",
            }}
          >
            <th
              style={{
                padding: "12px 8px",
                fontWeight: 600,
                fontSize: "0.875rem",
                color: "var(--mantine-color-dimmed)",
              }}
            >
              Credit
            </th>
            <th
              style={{
                padding: "12px 8px",
                fontWeight: 600,
                fontSize: "0.875rem",
                color: "var(--mantine-color-dimmed)",
              }}
            >
              People
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedCreditTypes.map(([creditType, creditedPeople]) => (
            <tr
              key={creditType}
              style={{
                borderBottom: "1px solid var(--mantine-color-default-border)",
              }}
            >
              <td
                style={{
                  padding: "12px 8px",
                  textTransform: "capitalize",
                  verticalAlign: "top",
                }}
              >
                {creditType}
              </td>
              <td style={{ padding: "12px 8px" }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {creditedPeople
                    .sort((a, b) =>
                      a.producer_name.localeCompare(b.producer_name),
                    )
                    .map((credit) => (
                      <CreditArtist
                        key={credit.producer_key}
                        credit={credit}
                      />
                    ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CreditArtist({ credit }: { credit: Credit }) {
  if (credit.artist_uri) {
    const artist = {
      artist_uri: credit.artist_uri,
      artist_name: credit.producer_name,
      artist_image_url: credit.artist_image_url || "",
      artist_followers: 0,
      artist_liked_track_count: 0,
      artist_popularity: 0,
      artist_track_count: 0,
      artist_stream_count: 0,
    };
    return <ArtistPill artist={artist} />;
  }

  return (
    <div
      style={{
        padding: "4px 12px",
        borderRadius: "16px",
        backgroundColor: "var(--mantine-color-default-hover)",
        fontSize: "0.875rem",
      }}
    >
      {credit.producer_name || "Unknown Artist"}
    </div>
  );
}
