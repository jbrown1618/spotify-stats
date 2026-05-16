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

/** Returns true if every entry in the bar chart data has a total value of 1 or less. */
export function allBarValuesAreOne(
  data: { Liked: number; Unliked: number }[]
): boolean {
  return data.length > 0 && data.every((d) => d.Liked + d.Unliked <= 1);
}
