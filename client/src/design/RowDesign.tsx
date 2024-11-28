import { Paper, Pill, Text } from "@mantine/core";
import { KPI, KPIProps } from "./KPI";

interface RowDesignProps {
  src: string;
  secondarySrc?: string;
  primaryText: string | JSX.Element;
  secondaryText?: string | JSX.Element;
  tertiaryText?: string | JSX.Element;
  labels?: string[];
  stats?: KPIProps[];
  onClick?: () => void;
}

export function RowDesign({
  src,
  secondarySrc,
  primaryText,
  secondaryText,
  tertiaryText,
  labels,
  stats,
  onClick,
}: RowDesignProps) {
  return (
    <Paper
      onClick={onClick}
      style={{
        position: "relative",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: 4,
        overflow: "hidden",
        cursor: onClick ? "pointer" : undefined,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          opacity: 0.15,
          backgroundImage: `url(${secondarySrc ?? src})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <img src={src} style={{ height: 70 }} />
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <Text fw={700}>{primaryText}</Text>
            {labels?.map((labelText) => (
              <Pill bg="gray">{labelText}</Pill>
            ))}
          </div>
          {typeof secondaryText === "string" ? (
            <Text>{secondaryText}</Text>
          ) : (
            secondaryText
          )}
          {typeof tertiaryText === "string" ? (
            <Text c="dimmed">{tertiaryText}</Text>
          ) : (
            tertiaryText
          )}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: 16,
          alignItems: "start",
          paddingRight: 8,
        }}
      >
        {stats?.map((stat) => (
          <KPI {...stat} />
        ))}
      </div>
    </Paper>
  );
}
