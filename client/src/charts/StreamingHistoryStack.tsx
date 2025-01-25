export function StreamingHistoryStack({
  data,
  renderKey,
}: {
  data: Record<string, Record<number, Record<number, number>>>;
  renderKey: (key: string) => JSX.Element;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      {Object.keys(data).map(renderKey)}
    </div>
  );
}
