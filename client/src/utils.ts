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
