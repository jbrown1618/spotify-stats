import {
  Card,
  Group,
  SimpleGrid,
  Skeleton,
  Stack,
  Text,
} from "@mantine/core";

import { useTracks } from "../useApi";
import { useSetFilters } from "../useFilters";
import styles from "./WrappedDetails.module.css";

interface MonthRange {
  end: string;
  label: string;
  start: string;
}

function toDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function toDateString(date: Date) {
  return date.toISOString().slice(0, 10);
}

function getMonthRanges(wrapped: string): MonthRange[] {
  const [startValue, endValue] = wrapped.split("..");
  if (!startValue || !endValue) return [];

  const start = toDate(startValue);
  const end = toDate(endValue);
  if (
    Number.isNaN(start.getTime()) ||
    Number.isNaN(end.getTime()) ||
    start >= end
  ) {
    return [];
  }

  const ranges: MonthRange[] = [];
  let cursor = start;

  while (cursor < end) {
    const nextMonth = new Date(
      Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1)
    );
    const rangeEnd = nextMonth < end ? nextMonth : end;

    ranges.push({
      start: toDateString(cursor),
      end: toDateString(rangeEnd),
      label: cursor.toLocaleDateString(undefined, {
        month: "long",
        timeZone: "UTC",
        year: "numeric",
      }),
    });
    cursor = rangeEnd;
  }

  return ranges;
}

function MonthTopTracks({ month }: { month: MonthRange }) {
  const setFilters = useSetFilters();
  const { items, isLoading } = useTracks({
    filters: { wrapped: `${month.start}..${month.end}` },
    limit: 10,
    sort: "Most streams",
  });

  return (
    <Card withBorder radius="md" padding="lg">
      <Text component="h3" fw={700} size="lg" mb="md">
        {month.label}
      </Text>
      {isLoading ? (
        <Stack gap="sm">
          {Array.from({ length: 10 }, (_, index) => (
            <Skeleton key={index} height={32} radius="sm" />
          ))}
        </Stack>
      ) : items?.length ? (
        <Stack gap={0}>
          {items.map((track, index) => (
            <button
              className={styles.track}
              key={track.track_uri}
              onClick={() => setFilters({ tracks: [track.track_uri] })}
              type="button"
            >
              <Text c="dimmed" className={styles.rank} size="sm">
                {index + 1}
              </Text>
              <div className={styles.trackDetails}>
                <Text fw={500} lineClamp={1}>
                  {track.track_short_name}
                </Text>
                <Text c="dimmed" lineClamp={1} size="sm">
                  {Object.values(track.artist_names).join(", ")}
                </Text>
              </div>
              <Text c="dimmed" size="sm">
                {track.track_stream_count.toLocaleString()}
              </Text>
            </button>
          ))}
        </Stack>
      ) : (
        <Text c="dimmed" fs="italic">
          No streams
        </Text>
      )}
    </Card>
  );
}

export function WrappedDetails({ wrapped }: { wrapped: string }) {
  const months = getMonthRanges(wrapped);
  if (months.length <= 1) return null;

  return (
    <section>
      <Group justify="space-between" mb="md">
        <Text component="h3" fw={700} size="xl">
          Top tracks by month
        </Text>
        <Text c="dimmed" size="sm">
          Streams
        </Text>
      </Group>
      <SimpleGrid cols={{ base: 1, md: 2 }}>
        {months.map((month) => (
          <MonthTopTracks key={month.start} month={month} />
        ))}
      </SimpleGrid>
    </section>
  );
}
