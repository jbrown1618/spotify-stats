import { Card, Skeleton, Text } from "@mantine/core";

import { KPIProps, KPIsList } from "./KPI";
import { SpotifyLink } from "./SpotifyLink";
import styles from "./TileDesign.module.css";

interface TileDesignProps {
  title: string;
  subtitle?: string;
  src: string;
  itemURI: string;
  stats?: KPIProps[];
  onClick: () => void;
}

export function TileDesign({
  onClick,
  title,
  subtitle,
  src,
  itemURI,
  stats,
}: TileDesignProps) {
  return (
    <Card
      w={150}
      shadow="md"
      withBorder
      className={styles.tile}
      onClick={onClick}
    >
      <Card.Section
        h={150}
        style={{
          backgroundImage: `url(${src})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />

      <div className={styles.tileContent}>
        <Text fw={700}>{title}</Text>
        {subtitle && <Text>{subtitle}</Text>}
        {stats && <KPIsList items={stats} />}
        <SpotifyLink text="Open" uri={itemURI} />
      </div>
    </Card>
  );
}

export function TileSkeleton() {
  return <Skeleton w={150} h={175} />;
}
