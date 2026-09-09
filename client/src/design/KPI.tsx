import { Skeleton, Text } from "@mantine/core";
import clsx from "clsx";

import styles from "./KPI.module.css";

export interface KPIProps {
  label: string;
  value: number | string | JSX.Element;
  compact?: boolean;
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

export function KPIsListSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className={styles.kpisList}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={styles.kpi}>
          <Skeleton w={60} h={14} mb={6} />
          <Skeleton w={80} h={24} />
        </div>
      ))}
    </div>
  );
}

export function KPI({ label, value, compact }: KPIProps) {
  return (
    <div className={clsx(styles.kpi, compact && styles.compact)}>
      <Text c="dimmed" className={clsx(styles.noWrap, styles.label)}>
        {label}
      </Text>
      {typeof value === "string" || typeof value === "number" ? (
        <Text size="xl" className={clsx(styles.noWrap, styles.value)}>
          {value}
        </Text>
      ) : (
        value
      )}
    </div>
  );
}
