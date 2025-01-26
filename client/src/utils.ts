export function formatDate(ts: number | undefined) {
  if (!ts) return "Unknown Date";
  const date = new Date(ts);
  return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
}

export function formatMonth(ts: number | undefined) {
  if (!ts) return "Unknown Date";
  const date = new Date(ts);
  return `${date.getFullYear()}-${date.getMonth() + 1}`;
}
