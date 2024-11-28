import { Text } from "@mantine/core";

export interface KPIProps {
  label: string;
  value: number | string | JSX.Element;
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
      <Text c="dimmed">{label}</Text>
      {typeof value === "string" || typeof value === "number" ? (
        <Text size={"xl"}>{value}</Text>
      ) : (
        value
      )}
    </div>
  );
}
