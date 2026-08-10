import { Text } from "@mantine/core";
import { IconHeart, IconHeartFilled } from "@tabler/icons-react";
import clsx from "clsx";
import { Fragment } from "react/jsx-runtime";

import { Track } from "../api";
import { KPIProps } from "../design/KPI";
import { RowDesign } from "../design/RowDesign";
import { useSetFilters } from "../useFilters";
import { useIsMobile } from "../useIsMobile";
import sharedStyles from "./ListItems.module.css";

interface TrackRowProps {
  track: Track;
  kpis?: (track: Track) => (KPIProps | null)[];
}

export function TrackRow({ track, kpis }: TrackRowProps) {
  const setFilters = useSetFilters();
  const isMobile = useIsMobile();

  const stats = kpis
    ? kpis(track)
    : [
        { label: "Streams", value: track.track_stream_count ?? 0 },
        isMobile
          ? null
          : { label: "Popularity", value: track.track_popularity },
        {
          label: "Liked",
          value: track.track_liked ? (
            <IconHeartFilled
              title="Liked"
              className={clsx(sharedStyles.likedIcon, sharedStyles.likedIconGreen)}
            />
          ) : (
            <IconHeart
              title="Liked"
              className={clsx(sharedStyles.likedIcon, sharedStyles.likedIconGray)}
            />
          ),
        },
      ];

  return (
    <RowDesign
      src={track.album_image_url}
      itemURI={track.album_uri}
      primaryText={isMobile ? track.track_short_name : track.track_name}
      secondaryText={isMobile ? track.album_short_name : track.album_name}
      onClick={() =>
        setFilters({
          tracks: [track.track_uri],
        })
      }
      tertiaryText={
        <div className={sharedStyles.artistsList}>
          {Object.values(track.artist_names).map((artist_name, i) => {
            return (
              <Fragment key={artist_name}>
                <Text c="dimmed">{artist_name}</Text>
                {i < Object.values(track.artist_names).length - 1 ? (
                  <Text c="dimmed">,&nbsp;</Text>
                ) : null}
              </Fragment>
            );
          })}
        </div>
      }
      stats={stats}
    />
  );
}
