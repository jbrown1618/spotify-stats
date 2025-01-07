import { Card, Skeleton, Text } from "@mantine/core";

import { KPIProps, KPIsList } from "./KPI";
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
      style={{ padding: 10, cursor: "pointer" }}
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
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            position: "relative",
            top: -150,
            marginBottom: -150,
          }}
        >
          <img
            src={src}
            style={{
              height: 200,
              width: 200,
              borderRadius: 100,
            }}
          />
        </div>
      )}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          paddingTop: 8,
        }}
      >
        <Text size={"xl"} fw={700}>
          {title}
        </Text>
        {subtitle && <Text>{subtitle}</Text>}
        {stats && <KPIsList items={stats} />}
        <SpotifyLink uri={itemURI} />
      </div>
    </Card>
  );
}

export function LargeTileSkeleton() {
  return <Skeleton w={300} h={350} />;
}
