import { AlbumRank, ArtistRank, StreamsByMonth, TrackRank } from "./api";

export function formatDate(ts: number | Date | undefined) {
  if (!ts) return "Unknown Date";
  const date = new Date(ts);
  return date.toISOString().split("T")[0];
}

export function formatMonth(ts: number | Date | undefined) {
  if (!ts) return "Unknown Date";
  const date = new Date(ts);
  return `${date.getFullYear()}-${date.getMonth() + 1}`;
}

export function addMonths(date: Date, months: number): Date {
  const newDate = new Date(date.getTime());
  newDate.setMonth(date.getMonth() + months);
  return newDate;
}

export function countUniqueMonths(streamsByMonth: StreamsByMonth) {
  const months = new Set<string>();
  for (const byYear of Object.values(streamsByMonth)) {
    for (const [year, byMonth] of Object.entries(byYear)) {
      for (const month of Object.keys(byMonth)) {
        months.add(`${year}-${month}`);
      }
    }
  }
  return months.size;
}

export function countUniqueAsOfDates(
  history: (ArtistRank | AlbumRank | TrackRank)[]
) {
  return new Set(history.map((value) => value.as_of_date)).size;
}

const minYear = 2020; // Whatever, just hard-code it.

export function namedWrappedOptions() {
  const currentYear = new Date().getFullYear();

  const years = [];
  for (let i = minYear; i <= currentYear; ++i) {
    years.push(i);
  }

  const beginningOfThisMonth = new Date(
    new Date().getFullYear(),
    new Date().getMonth(),
    1
  );
  const beginningOfNextMonth = addMonths(beginningOfThisMonth, 1);
  const sixMonthsAgo = addMonths(beginningOfThisMonth, -6);

  return [
    {
      label: "This month",
      value: `${formatDate(beginningOfThisMonth)}..${formatDate(
        beginningOfNextMonth
      )}`,
    },
    {
      label: "Last 6 months",
      value: `${formatDate(sixMonthsAgo)}..${formatDate(beginningOfNextMonth)}`,
    },
    ...years.reverse().map((y) => ({
      label: `${y}`,
      value: `${y}-01-01..${y + 1}-01-01`,
    })),
  ];
}
