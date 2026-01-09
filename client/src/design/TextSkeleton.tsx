import { Skeleton } from "@mantine/core";

import styles from "./TextSkeleton.module.css";

export function TextSkeleton({ style }: { style: keyof typeof styleMap }) {
  const { height, lineHeight, marginY, width } = styleMap[style];
  return (
    <div
      className={styles.textSkeleton}
      style={{
        height: lineHeight,
        marginTop: marginY,
        marginBottom: marginY,
      }}
    >
      <Skeleton width={width} height={height} />
    </div>
  );
}

const styleMap = {
  regular: {
    height: 14,
    lineHeight: 24,
    marginY: 0,
    width: 100,
  },
  h2: {
    height: 26,
    lineHeight: 36,
    marginY: 20,
    width: 200,
  },
  h3: {
    height: 24,
    lineHeight: 30,
    marginY: 19,
    width: 200,
  },
};
