import { Text } from "@mantine/core";

import styles from "./KPI.module.css";

export interface KPIProps {
  label: string;
  value: number | string | JSX.Element;
}

export function KPIsList({ items }: { items: KPIProps[] }) {
  return (
    <div className={styles.kpisList}>
      {items.map((kpi) => (
        <KPI key={kpi.label} {...kpi} />
      ))}
    </div>
  );
}

export function KPI({ label, value }: KPIProps) {
  return (
    <div className={styles.kpi}>
      <Text c="dimmed" className={styles.noWrap}>
        {label}
      </Text>
      {typeof value === "string" || typeof value === "number" ? (
        <Text size={"xl"} className={styles.noWrap}>
          {value}
        </Text>
      ) : (
        value
      )}
    </div>
  );
}
