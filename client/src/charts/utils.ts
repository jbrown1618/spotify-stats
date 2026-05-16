/** Sum all stream counts across all years and months for an entity. */
export function totalStreams(
  byYear: Record<number, Record<number, number>> | undefined
): number {
  if (!byYear) return 0;
  return Object.values(byYear).reduce(
    (sum, byMonth) =>
      sum + Object.values(byMonth).reduce((s, count) => s + count, 0),
    0
  );
}
