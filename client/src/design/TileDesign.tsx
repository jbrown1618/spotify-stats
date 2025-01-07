import { Card, Skeleton, Text } from "@mantine/core";

import { KPIProps, KPIsList } from "./KPI";
import { SpotifyLink } from "./SpotifyLink";

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
      style={{ padding: 10, cursor: "pointer" }}
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

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: 8,
        }}
      >
        <Text fw={700}>{title}</Text>
        {subtitle && <Text>{subtitle}</Text>}
        {stats && <KPIsList items={stats} />}
        <SpotifyLink uri={itemURI} />
      </div>
    </Card>
  );
}

export function TileSkeleton() {
  return <Skeleton w={150} h={175} />;
}
