export interface MonthRange {
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

export function getWrappedMonthRanges(wrapped: string): MonthRange[] {
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

export function isMultiMonthWrapped(wrapped: string | undefined) {
  return wrapped ? getWrappedMonthRanges(wrapped).length > 1 : false;
}
