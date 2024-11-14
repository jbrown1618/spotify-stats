import { Card } from "@mantine/core";

interface TileDesignProps {
  title: string;
  stats?: Stat[];
  src: string;
  secondarySrc?: string;
  onClick: () => void;
}

interface Stat {
  value: number;
  label: string;
}

export function TileDesign({ onClick, title, src }: TileDesignProps) {
  return (
    <Card
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
      <div style={{ display: "flex", flexDirection: "column" }}>{title}</div>
    </Card>
  );
}
