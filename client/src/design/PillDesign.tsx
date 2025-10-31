import { Pill, Skeleton } from "@mantine/core";
import clsx from "clsx";
import { PropsWithChildren } from "react";

import styles from "./PillDesign.module.css";

export function PillSkeleton() {
  return <Skeleton h={30} w={150} radius={15} />;
}

export function PillWithAvatar({
  imageHref,
  onClick,
  children,
}: PropsWithChildren<{ imageHref: string; onClick?: () => void }>) {
  return (
    <Pill
      size="lg"
      className={clsx(styles.pill, onClick && styles.clickable)}
      onClick={onClick}
    >
      <img className={styles.avatar} src={imageHref} />
      <span className={styles.label}>{children}</span>
    </Pill>
  );
}
