import { Card, SegmentedControl, Skeleton, Stack, Text } from "@mantine/core";
import { useState } from "react";

import { Album, Artist, Track } from "../api";
import { useAlbums, useArtists, useTracks } from "../useApi";
import { useSetFilters } from "../useFilters";
import { getWrappedMonthRanges, MonthRange } from "../wrapped";
import styles from "./WrappedDetails.module.css";

type RankingType = "tracks" | "artists" | "albums";

interface RankingItem {
  uri: string;
  name: string;
  subtitle?: string;
  imageUrl?: string;
  streams: number;
  filters: { tracks?: string[]; artists?: string[]; albums?: string[] };
}

function rankingItems(
  items: Track[] | Artist[] | Album[] | undefined,
  type: RankingType
): RankingItem[] {
  if (!items) return [];

  return items.map((item) => {
    if (type === "tracks") {
      const track = item as Track;
      return {
        uri: track.track_uri,
        name: track.track_short_name,
        subtitle: track.artist_names.join(", "),
        imageUrl: track.album_image_url,
        streams: track.track_stream_count,
        filters: { tracks: [track.track_uri] },
      };
    }

    if (type === "artists") {
      const artist = item as Artist;
      return {
        uri: artist.artist_uri,
        name: artist.artist_name,
        streams: artist.artist_stream_count,
        filters: { artists: [artist.artist_uri] },
      };
    }

    const album = item as Album;
    return {
      uri: album.album_uri,
      name: album.album_short_name,
      streams: album.album_stream_count,
      filters: { albums: [album.album_uri] },
    };
  });
}

function RankingList({
  items,
  isLoading,
  isError,
}: {
  items: RankingItem[];
  isLoading: boolean;
  isError: boolean;
}) {
  const setFilters = useSetFilters();

  if (isLoading) {
    return (
      <Stack gap="sm" aria-label="Loading top rankings">
        {Array.from({ length: 10 }, (_, index) => (
          <Skeleton key={index} height={32} radius="sm" />
        ))}
      </Stack>
    );
  }

  if (isError) {
    return (
      <Text c="dimmed" fs="italic">
        Could not load rankings
      </Text>
    );
  }

  if (!items.length) {
    return (
      <Text c="dimmed" fs="italic">
        No streams
      </Text>
    );
  }

  return (
    <Stack gap={0}>
      {items.map((item, index) => (
        <button
          className={styles.track}
          key={item.uri}
          onClick={() => setFilters(item.filters)}
          type="button"
        >
          {item.imageUrl ? (
            <img alt="" className={styles.albumImage} src={item.imageUrl} />
          ) : (
            <Text c="dimmed" className={styles.rank} size="sm">
              {index + 1}
            </Text>
          )}
          <div className={styles.trackDetails}>
            <Text fw={500} lineClamp={1}>
              {item.name}
            </Text>
            {item.subtitle && (
              <Text c="dimmed" lineClamp={1} size="sm">
                {item.subtitle}
              </Text>
            )}
          </div>
          <Text c="dimmed" size="sm">
            {item.streams.toLocaleString()}
          </Text>
        </button>
      ))}
    </Stack>
  );
}

function MonthTracks({ month }: { month: MonthRange }) {
  const { items, isLoading, isError } = useTracks({
    filters: { wrapped: `${month.start}..${month.end}` },
    limit: 10,
    sort: "Most streams",
  });

  return (
    <RankingList
      items={rankingItems(items, "tracks")}
      isLoading={isLoading}
      isError={isError}
    />
  );
}

function MonthArtists({ month }: { month: MonthRange }) {
  const { items, isLoading, isError } = useArtists({
    filters: { wrapped: `${month.start}..${month.end}` },
    limit: 10,
    sort: "Most streams",
  });

  return (
    <RankingList
      items={rankingItems(items, "artists")}
      isLoading={isLoading}
      isError={isError}
    />
  );
}

function MonthAlbums({ month }: { month: MonthRange }) {
  const { items, isLoading, isError } = useAlbums({
    filters: { wrapped: `${month.start}..${month.end}` },
    limit: 10,
    sort: "Most streams",
  });

  return (
    <RankingList
      items={rankingItems(items, "albums")}
      isLoading={isLoading}
      isError={isError}
    />
  );
}

function MonthCard({
  month,
  type,
}: {
  month: MonthRange;
  type: RankingType;
}) {
  return (
    <Card
      aria-label={`${month.label} top ${type}`}
      className={styles.monthCard}
      component="article"
      padding="md"
      radius="md"
      withBorder
    >
      <Text component="h3" fw={700} size="lg" mb="md">
        {month.label}
      </Text>
      {type === "tracks" ? (
        <MonthTracks month={month} />
      ) : type === "artists" ? (
        <MonthArtists month={month} />
      ) : (
        <MonthAlbums month={month} />
      )}
    </Card>
  );
}

export function WrappedDetails({ wrapped }: { wrapped: string }) {
  const months = getWrappedMonthRanges(wrapped);
  const [type, setType] = useState<RankingType>("tracks");

  return (
    <section>
      <Text component="h3" fw={700} size="xl" mb="md">
        Top 10 by month
      </Text>
      <SegmentedControl
        aria-label="Ranking type"
        className={styles.rankingTypes}
        data={[
          { label: "Tracks", value: "tracks" },
          { label: "Artists", value: "artists" },
          { label: "Albums", value: "albums" },
        ]}
        onChange={(value) => setType(value as RankingType)}
        value={type}
      />
      {months.length ? (
        <div aria-label="Monthly top 10 cards" className={styles.carousel}>
          {months.map((month) => (
            <MonthCard key={month.start} month={month} type={type} />
          ))}
        </div>
      ) : (
        <Text c="dimmed" fs="italic">
          Select a valid date range to view monthly rankings.
        </Text>
      )}
    </section>
  );
}
