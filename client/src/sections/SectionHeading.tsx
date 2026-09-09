import { Pill } from "@mantine/core";

import styles from "./Sections.module.css";

interface SectionHeadingProps {
  title: string;
  total: number;
}

export function SectionHeading({ title, total }: SectionHeadingProps) {
  return (
    <div className={styles.sectionHeading}>
      <h2>{title}</h2>
      <Pill size="lg">{total.toLocaleString()}</Pill>
    </div>
  );
}
