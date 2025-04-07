import { Text } from "@mantine/core";
import { IconHeart, IconHeartFilled } from "@tabler/icons-react";

import { RowDesign } from "../design/RowDesign";
import { useArtists, useTrack } from "../useApi";
import { useIsMobile } from "../useIsMobile";

interface TrackRowProps {
  trackUri: string;
}

export function TrackRow({ trackUri }: TrackRowProps) {
  const { data: track } = useTrack(trackUri);
  const { data: artists } = useArtists([trackUri]);
  const isMobile = useIsMobile();

  if (!track) return; // TODO: skeleton
  return (
    <RowDesign
      src={track.album_image_url}
      itemURI={track.album_uri}
      primaryText={isMobile ? track.track_short_name : track.track_name}
      secondaryText={isMobile ? track.album_short_name : track.album_name}
      tertiaryText={
        <div style={{ display: "flex" }}>
          {!artists
            ? null /* TODO: skeleton */
            : Object.values(artists).map((artist, i) => {
                return (
                  <>
                    <Text c="dimmed">{artist.artist_name}</Text>
                    {i < Object.values(artists).length - 1 ? (
                      <Text c="dimmed">,&nbsp;</Text>
                    ) : null}
                  </>
                );
              })}
        </div>
      }
      stats={[
        isMobile ? null : { label: "Rank", value: track.track_rank },
        { label: "Streams", value: track.track_stream_count },
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
