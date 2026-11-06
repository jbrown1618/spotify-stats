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
import { getWrappedMonthRanges, MonthRange } from "../wrapped";
import styles from "./WrappedDetails.module.css";

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
  const months = getWrappedMonthRanges(wrapped);

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
