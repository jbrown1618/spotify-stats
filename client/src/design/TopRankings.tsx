import { Paper, Text, ThemeIcon, Title } from "@mantine/core";
import { IconTrophy } from "@tabler/icons-react";

import type { RankingEntityType } from "../api";
import { useTopRankings } from "../useApi";
import styles from "./TopRankings.module.css";

const entityLabels: Record<RankingEntityType, string> = {
  track: "track",
  artist: "artist",
  album: "album",
};

interface TopRankingsProps {
  entityType: RankingEntityType;
  uri: string;
}

export function TopRankings({
  entityType,
  uri,
}: TopRankingsProps) {
  const { data: rankings } = useTopRankings(entityType, uri);

  if (!rankings?.length) return null;

  const entityLabel = entityLabels[entityType];

  return (
    <Paper withBorder radius="md" className={styles.section}>
      <div className={styles.heading}>
        <ThemeIcon color="yellow" variant="light" radius="xl" size="lg">
          <IconTrophy size={20} />
        </ThemeIcon>
        <Title order={3}>Top 100 rankings</Title>
      </div>
      <div className={styles.rankings}>
        {rankings.map(({ rank, year }) => (
          <Text key={year} className={styles.ranking}>
            #{rank} {entityLabel} of {year ?? "all time"}
          </Text>
        ))}
      </div>
    </Paper>
  );
}
