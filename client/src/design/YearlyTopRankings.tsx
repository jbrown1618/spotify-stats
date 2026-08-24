import { Paper, Text, ThemeIcon, Title } from "@mantine/core";
import { IconTrophy } from "@tabler/icons-react";

import type { RankingEntityType } from "../api";
import { useYearlyRankings } from "../useApi";
import styles from "./YearlyTopRankings.module.css";

const entityLabels: Record<RankingEntityType, string> = {
  track: "track",
  artist: "artist",
  album: "album",
};

interface YearlyTopRankingsProps {
  entityType: RankingEntityType;
  uri: string;
}

export function YearlyTopRankings({
  entityType,
  uri,
}: YearlyTopRankingsProps) {
  const { data: rankings } = useYearlyRankings(entityType, uri);

  if (!rankings?.length) return null;

  const entityLabel = entityLabels[entityType];

  return (
    <Paper withBorder radius="md" className={styles.section}>
      <div className={styles.heading}>
        <ThemeIcon color="yellow" variant="light" radius="xl" size="lg">
          <IconTrophy size={20} />
        </ThemeIcon>
        <Title order={3}>Top 100 by year</Title>
      </div>
      <div className={styles.rankings}>
        {rankings.map(({ rank, year }) => (
          <Text key={year} className={styles.ranking}>
            #{rank} {entityLabel} of {year}
          </Text>
        ))}
      </div>
    </Paper>
  );
}
