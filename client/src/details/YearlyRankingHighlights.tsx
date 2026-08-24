import { Badge, Group, Paper, Stack, Title } from "@mantine/core";

import type { RankingEntityType } from "../api";
import { useYearlyRankings } from "../useApi";

interface YearlyRankingHighlightsProps {
  entityType: RankingEntityType;
  entityURI: string;
}

export function YearlyRankingHighlights({
  entityType,
  entityURI,
}: YearlyRankingHighlightsProps) {
  const { data: rankings } = useYearlyRankings(entityType, entityURI);

  if (!rankings?.length) return null;

  return (
    <Paper withBorder p="lg" radius="md" mt="xl">
      <Stack gap="sm">
        <Title order={3}>Top yearly rankings</Title>
        <Group gap="sm">
          {rankings.map((ranking) => (
            <Badge
              key={ranking.year}
              size="lg"
              variant="light"
              radius="sm"
              tt="none"
            >
              #{ranking.yearly_rank} {entityType} of {ranking.year}
            </Badge>
          ))}
        </Group>
      </Stack>
    </Paper>
  );
}
