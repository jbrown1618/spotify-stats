import { Paper, Pill, Skeleton, Text } from "@mantine/core";
import clsx from "clsx";

import { useIsMobile } from "../useIsMobile";
import { KPI, KPIProps } from "./KPI";
import styles from "./RowDesign.module.css";
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
      className={clsx(styles.row, onClick && styles.rowClickable)}
    >
      <div
        className={styles.rowBackground}
        style={{ backgroundImage: `url(${secondarySrc ?? src})` }}
      />
      <div className={styles.rowContent}>
        <img src={src} className={styles.rowImage} />
        <div className={styles.rowText}>
          <div className={styles.rowTextPrimary}>
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

      <div className={styles.rowStats}>
        {stats?.map((stat) =>
          stat ? <KPI key={stat.label} {...stat} /> : null
        )}
        {!isMobile && (
          <KPI
            value={
              <div className={styles.spotifyLinkContainer}>
                <SpotifyLink uri={itemURI} size={20} />
              </div>
            }
            label="Open"
          />
        )}
      </div>
      {isMobile && (
        <div className={styles.spotifyLinkMobile}>
          <SpotifyLink uri={itemURI} />
        </div>
      )}
    </Paper>
  );
}

export function RowSkeleton() {
  return <Skeleton w={"100%"} h={80} />;
}
