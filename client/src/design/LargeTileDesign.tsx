import { Card, Skeleton, Text } from "@mantine/core";

import { KPIProps, KPIsList } from "./KPI";
import styles from "./LargeTileDesign.module.css";
import { SpotifyLink } from "./SpotifyLink";

interface LargeTileDesignProps {
  title: string;
  subtitle?: string;
  stats?: KPIProps[];
  src: string;
  secondarySrc?: string;
  itemURI: string;
  onClick: () => void;
}

export function LargeTileDesign({
  onClick,
  title,
  subtitle,
  src,
  stats,
  secondarySrc,
  itemURI,
}: LargeTileDesignProps) {
  return (
    <Card
      w={300}
      shadow="md"
      withBorder
      className={styles.largeTile}
      onClick={onClick}
    >
      <Card.Section
        h={200}
        style={{
          backgroundImage: `url(${secondarySrc ?? src})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />
      {secondarySrc && (
        <div className={styles.largeTileImageContainer}>
          <img src={src} className={styles.largeTileImage} />
        </div>
      )}
      <div className={styles.largeTileContent}>
        <Text size={"xl"} fw={700}>
          {title}
        </Text>
        {subtitle && <Text>{subtitle}</Text>}
        {stats && <KPIsList items={stats} />}
        <SpotifyLink text="Open" uri={itemURI} />
      </div>
    </Card>
  );
}

export function LargeTileSkeleton() {
  return <Skeleton w={300} h={350} />;
}
