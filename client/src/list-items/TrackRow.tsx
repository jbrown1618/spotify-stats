import { Text } from "@mantine/core";
import { IconHeart, IconHeartFilled } from "@tabler/icons-react";
import { Fragment } from "react/jsx-runtime";

import { RowDesign, RowSkeleton } from "../design/RowDesign";
import { useTrack } from "../useApi";
import { useSetFilters } from "../useFilters";
import { useIsMobile } from "../useIsMobile";

interface TrackRowProps {
  trackUri: string;
}

export function TrackRow({ trackUri }: TrackRowProps) {
  const setFilters = useSetFilters();
  const { data: track } = useTrack(trackUri);
  const isMobile = useIsMobile();

  if (!track) return <RowSkeleton />;

  return (
    <RowDesign
      src={track.album_image_url}
      itemURI={track.album_uri}
      primaryText={isMobile ? track.track_short_name : track.track_name}
      secondaryText={isMobile ? track.album_short_name : track.album_name}
      onClick={() =>
        setFilters({
          tracks: [trackUri],
        })
      }
      tertiaryText={
        <div style={{ display: "flex" }}>
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
      stats={[
        { label: "Streams", value: track.track_stream_count ?? 0 },
        isMobile
          ? null
          : { label: "Popularity", value: track.track_popularity },
        {
          label: "Liked",
          value: track.track_liked ? (
            <IconHeartFilled
              title="Liked"
              style={{ color: "green", marginTop: 4 }}
            />
          ) : (
            <IconHeart
              title="Unliked"
              style={{ color: "gray", marginTop: 4 }}
            />
          ),
        },
      ]}
    />
  );
}
