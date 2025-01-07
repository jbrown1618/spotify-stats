import { Text } from "@mantine/core";

export interface KPIProps {
  label: string;
  value: number | string | JSX.Element;
}

export function KPIsList({ items }: { items: KPIProps[] }) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "space-evenly",
        gap: 16,
      }}
    >
      {items.map((kpi) => (
        <KPI {...kpi} />
      ))}
    </div>
  );
}

export function KPI({ label, value }: KPIProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <Text c="dimmed" style={{ textWrap: "nowrap" }}>
        {label}
      </Text>
      {typeof value === "string" || typeof value === "number" ? (
        <Text size={"xl"} style={{ textWrap: "nowrap" }}>
          {value}
        </Text>
      ) : (
        value
      )}
    </div>
  );
}
