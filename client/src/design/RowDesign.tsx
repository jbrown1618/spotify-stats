import { Paper, Pill, Skeleton, Text } from "@mantine/core";

import { useIsMobile } from "../useIsMobile";
import { KPI, KPIProps } from "./KPI";
import { SpotifyLink } from "./SpotifyLink";

interface RowDesignProps {
  src: string;
  primaryText: string | JSX.Element;
  itemURI: string;
  secondarySrc?: string;
  secondaryText?: string | JSX.Element;
  tertiaryText?: string | JSX.Element;
  labels?: string[];
  stats?: (KPIProps | null)[];
  onClick?: () => void;
}

export function RowDesign({
  src,
  itemURI,
  secondarySrc,
  primaryText,
  secondaryText,
  tertiaryText,
  labels,
  stats,
  onClick,
}: RowDesignProps) {
  const isMobile = useIsMobile();
  return (
    <Paper
      onClick={onClick}
      style={{
        width: "100%",
        position: "relative",
        display: "flex",
        gap: 16,
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
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          flexShrink: 1,
          overflow: "hidden",
          textOverflow: "ellipsis",
          position: "relative",
        }}
      >
        <img src={src} style={{ height: 70 }} />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            whiteSpace: "nowrap",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 8,
              alignItems: "center",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
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
          flexShrink: 0,
          display: "flex",
          gap: 16,
          alignItems: "start",
          paddingRight: 8,
          position: "relative",
        }}
      >
        {stats?.map((stat) =>
          stat ? <KPI key={stat.label} {...stat} /> : null
        )}
        {!isMobile && (
          <KPI
            value={
              <div style={{ marginTop: 5 }}>
                <SpotifyLink uri={itemURI} size={20} />
              </div>
            }
            label="Open"
          />
        )}
      </div>
      {isMobile && (
        <div
          style={{
            position: "absolute",
            left: 7,
            bottom: 3,
          }}
        >
          <SpotifyLink uri={itemURI} />
        </div>
      )}
    </Paper>
  );
}

export function RowSkeleton() {
  return <Skeleton w={"100%"} h={80} />;
}
