import { Card, Text } from "@mantine/core";

interface TileDesignProps {
  title: string;
  src: string | string[];
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
      {Array.isArray(src) ? (
        <Card.Section style={{ display: "flex", flexWrap: "wrap" }}>
          {src.map((url) => (
            <img src={url} height="50%" width="50%" />
          ))}
        </Card.Section>
      ) : src.length < 4 ? (
        <Card.Section
          h={150}
          style={{
            backgroundImage: `url(${src[0]})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
      ) : (
        <Card.Section
          h={150}
          style={{
            backgroundImage: `url(${src})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
      )}

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
