import { Card, Skeleton, Text } from "@mantine/core";

interface TileDesignProps {
  title: string;
  src: string;
  onClick: () => void;
}

export function TileDesign({ onClick, title, src }: TileDesignProps) {
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
      </div>
    </Card>
  );
}

export function TileSkeleton() {
  return <Skeleton w={150} h={175} />;
}
